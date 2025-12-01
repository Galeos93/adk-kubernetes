from typing import Callable, Dict
import json
import logging

from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from redis import Redis
from vyper import v


logger = logging.getLogger(__name__)


class BaseGmailCallback:
    def __init__(self, auth_scheme, auth_credential):
        self.redis_client = Redis.from_url(v.get("redis.url")) if v.get("redis.url") else None
        self._uuid_separator = "-"
        self._session_user_separator = ":"
        self._auth_scheme = auth_scheme
        self._auth_credential = auth_credential

    def get_credential_key_from_auth_scheme_and_credential(
            self,
            auth_scheme,
            auth_credential,
    ) -> str:
        scheme_name = f"{auth_scheme.type_.name}_{hash(auth_scheme.model_dump_json())}"
        credential_name = f"{auth_credential.auth_type.value}_{hash(auth_credential.model_dump_json())}"
        credential_key = f"{scheme_name}_{credential_name}_existing_exchanged_credential"
        return credential_key

    def get_temporary_credential_key(
            self,
            auth_scheme,
            auth_credential,
    ) -> str:
        scheme_name = f"{auth_scheme.type_.name}_{hash(auth_scheme.model_dump_json())}"
        credential_name = f"{auth_credential.auth_type.value}_{hash(auth_credential.model_dump_json())}"
        credential_key = f"temp:adk_{scheme_name}_{credential_name}"
        return credential_key

    def get_persistent_credential_key(
            self,
            credential_key: str, # This is not same across subprocesses
            session_id: str,
            session_user_id: str,
            gmail_user_id: str,
    ) -> str:
        uuid = session_id + self._session_user_separator + session_user_id + self._session_user_separator + gmail_user_id
        credential_key_redis = f"{uuid}"
        return credential_key_redis
    
    def get_session_user_from_persistent_credential_key(
            self,
            credential_key_redis: str,
    ) -> tuple[str, str]:
        uuid = credential_key_redis.split(f"{self._uuid_separator}")[-1]
        session_id, user_id = uuid.split(self._session_user_separator)
        return session_id, user_id


class GmailToolBeforeCallback(BaseGmailCallback):
    def __init__(self, auth_scheme, auth_credential):
        super().__init__(auth_scheme, auth_credential)
        self._last_connection_input_user_id = None

    def _delete_stale_credential(
            self,
            tool_context: ToolContext,
            connector_input_user_id: str,
    ):
        if self._last_connection_input_user_id is None:
            # no previous user_id, therefore, no stale credential to delete
            return

        session = tool_context.session
        session_id = session.id
        session_user_id = session.user_id

        credential_key = self.get_credential_key_from_auth_scheme_and_credential(
            self._auth_scheme,
            self._auth_credential,
        )
        credential_key_redis = self.get_persistent_credential_key(
            credential_key,
            session_id,
            session_user_id,
            self._last_connection_input_user_id,
        )

        if self._last_connection_input_user_id != connector_input_user_id:
            # Delete stale credential from tool context state
            if credential_key in tool_context.state:
                tool_context.state[credential_key] = None

            # Delete stale credential from Redis
            if self.redis_client is not None:
                self.redis_client.delete(credential_key_redis)

            return

        # HACK: When the user access the e-mail with another account, the code above
        # succeds in removing the credential from the tool context. However, after the
        # user authenticates with the new account to delegate the access, the previous
        # credential remain for reasons I do not fully understand. So here I check
        # if the temp credential (set after Oauth2 flow) is different from the existing
        # one, and if so, I delete the existing one again.
        temp_credential_key = self.get_temporary_credential_key(
            self._auth_scheme,
            self._auth_credential,
        )
        duplicated_key = temp_credential_key.replace("temp:adk_", "") == credential_key.replace("_existing_exchanged_credential", "")
        temp_credential_is_none = tool_context.state.get(temp_credential_key) is None

        if temp_credential_is_none:
            return

        credential_value = tool_context.state.get(
            credential_key, {}).get("oauth2", {}).get("access_token")
        temp_credential_value = tool_context.state.get(
            temp_credential_key).model_dump().get(
                "oauth2", {}).get("access_token")

        if duplicated_key and credential_value != temp_credential_value:
            # This means the user completed Oauth2. Delete the state again
            if tool_context.state.get(credential_key) is not None:
                tool_context.state[credential_key] = None


    def __call__(self, tool: BaseTool, args: dict, tool_context: ToolContext):
        # FIXME: Temporarily rping the credential key and state
        credential_key = self.get_credential_key_from_auth_scheme_and_credential(
            self._auth_scheme,
            self._auth_credential,
        )

        # Rules: 
        # 1. Delete previous credential if userId in connector input payload has changed
        # 2. Load credential from Redis if exists and not set already in tool_context.state
        connector_input_user_id = args.get("connector_input_payload", {}).get("Path parameters", {}).get("userId")

        if connector_input_user_id is not None:
            self._delete_stale_credential(tool_context, connector_input_user_id)
            self._last_connection_input_user_id = connector_input_user_id
        else:
            # Cannot load credential from Redis without userId
            return

        credential_key = self.get_credential_key_from_auth_scheme_and_credential(
            self._auth_scheme,
            self._auth_credential,
        )

        persistent_credential_key = self.get_persistent_credential_key(
            credential_key,
            tool_context.session.id,
            tool_context.session.user_id,
            connector_input_user_id,
        )

        if tool_context.state.get(credential_key) is None:
            # Try to load from Redis
            if self.redis_client is not None:
                credential_data = self.redis_client.get(persistent_credential_key)
                if credential_data is not None:
                    logger.info("Loading credential from Redis for key: %s", persistent_credential_key)
                    credential_dict = json.loads(credential_data)
                    tool_context.state[credential_key] = credential_dict


class GmailToolAfterCallback(BaseGmailCallback):
    def __call__(self, tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict:
        session = tool_context.session
        session_id = session.id
        user_id = session.user_id

        connector_input_user_id = args.get("connector_input_payload", {}).get("Path parameters", {}).get("userId")

        if connector_input_user_id is None:
            return tool_response

        credential_key = self.get_credential_key_from_auth_scheme_and_credential(
            self._auth_scheme,
            self._auth_credential,
        )
        credential_key_redis = self.get_persistent_credential_key(
            credential_key,
            session_id,
            user_id,
            connector_input_user_id,
        )

        credential = tool_context.state.get(credential_key)

        if self.redis_client is not None and credential is not None:
            self.redis_client.set(credential_key_redis, json.dumps(credential))

        return tool_response


class BeforeToolCallback:
    def __init__(self, callbacks: dict[str, Callable[[BaseTool, dict, ToolContext], None]] = None):
        self._callbacks: dict[str, Callable[[BaseTool, dict, ToolContext], None]] = {
            **(callbacks or {})
        }
        self._default_callback = lambda tool, args, tool_context: None

    def register(self, tool_name: str, callback: Callable[[BaseTool, dict, ToolContext], None]):
        """Register a callback for a specific tool name."""
        self._callbacks[tool_name] = callback

    def __call__(self, tool: BaseTool, args: dict, tool_context: ToolContext):
        if tool.name in self._callbacks:
            self._callbacks[tool.name](tool, args, tool_context)
        else:
            self._default_callback(tool, args, tool_context)


class AfterToolCallback:
    def __init__(self, callbacks: dict[str, Callable[[BaseTool, dict, ToolContext, dict], dict]] = None):
        self._callbacks: dict[str, Callable[[BaseTool, dict, ToolContext, dict], dict]] = {
            **(callbacks or {})
        }
        self._default_callback = lambda tool, args, tool_context, tool_response: tool_response

    def register(self, tool_name: str, callback: Callable[[BaseTool, dict, ToolContext, dict], dict]):
        """Register a callback for a specific tool name."""
        self._callbacks[tool_name] = callback

    def __call__(self, tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict:
        if tool.name in self._callbacks:
            return self._callbacks[tool.name](tool, args, tool_context, tool_response)
        else:
            return self._default_callback(tool, args, tool_context, tool_response)