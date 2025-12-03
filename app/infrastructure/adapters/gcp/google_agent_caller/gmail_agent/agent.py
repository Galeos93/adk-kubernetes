import copy  # Add this import for deep copying
import json
import os
from pathlib import Path

if os.environ.get("DISABLE_IPV6", "True").lower() == "true":
    import requests

    requests.packages.urllib3.util.connection.HAS_IPV6 = False

from google.adk.agents.llm_agent import LlmAgent
from google.adk.auth.auth_credential import (
    AuthCredential,
    AuthCredentialTypes,
    OAuth2Auth,
)
from google.adk.tools.application_integration_tool.application_integration_toolset import (  # noqa: E501
    ApplicationIntegrationToolset,
)
from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme

from infrastructure.adapters.gcp.google_agent_caller.gmail_agent.callbacks import (
    AfterToolCallback,
    BeforeToolCallback,
    GmailToolAfterCallback,
    GmailToolBeforeCallback,
)

# --- Authentication Configuration ---
# This section configures how the agent will handle authentication using OpenID
# Connect (OIDC),
# often layered on top of OAuth 2.0.


# Define the Authentication Scheme using OpenID Connect.
# This object tells the ADK *how* to perform the OIDC/OAuth2 flow.
# It requires details specific to your Identity Provider (IDP), like Google OAuth,
# Okta, Auth0, etc.
# Note: Replace the example Okta URLs and credentials with your actual IDP details.
# All following fields are required, and available from your IDP.
def configure_google_oauth2_data(scopes: dict):
    oauth2_data_google_cloud = {
        "type": "oauth2",
        "flows": {
            "authorizationCode": {
                "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
                "tokenUrl": "https://oauth2.googleapis.com/token",
                "scopes": scopes,
            }
        },
    }

    auth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

    return auth_scheme


def load_service_account_credentials(sa_credentials_path: str) -> dict:
    with Path(sa_credentials_path).open("r") as f:
        sa_credentials = json.load(f)
    return sa_credentials


AUTH_SCHEME = configure_google_oauth2_data(
    scopes={
        "https://www.googleapis.com/auth/gmail.readonly": "View your emails in Gmail",
    }
)

# Define the Authentication Credentials for your specific application.
# This object holds the client identifier and secret that your application uses
# to identify itself to the IDP during the OAuth2 flow.
# !! SECURITY WARNING: Avoid hardcoding secrets in production code. !!
# !! Use environment variables or a secret management system instead. !!
AUTH_CREDENTIAL = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=os.environ["GOOGLE_APP_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_APP_CLIENT_SECRET"],
    ),
)

if os.getenv("INTEGRATION_CONNECTION_SA_CREDENTIALS") is None:
    SERVICE_ACCOUNT_JSON = None
else:
    SERVICE_ACCOUNT_JSON = json.dumps(
        load_service_account_credentials(
            os.environ["INTEGRATION_CONNECTION_SA_CREDENTIALS"]
        )
    )

connector_tool = ApplicationIntegrationToolset(
    project="agents-playground-474510",
    location="us-central1",  # TODO: replace with location of the connection
    connection="gmail-connection",  # TODO: replace with connection name
    entity_operations={"Entity_One": ["LIST", "CREATE"], "Entity_Two": []},
    actions=[
        "GET_gmail/v1/users/%7BuserId%7D/messages",
        "GET_gmail/v1/users/%7BuserId%7D/messages/%7Bid%7D",
    ],  # TODO: replace with actions. this one is for list events
    service_account_json=SERVICE_ACCOUNT_JSON,
    tool_name_prefix="",
    tool_instructions="List e-mails from user and retrieve e-mail details",
    auth_scheme=AUTH_SCHEME,
    auth_credential=AUTH_CREDENTIAL,
)


# Gmail-specific callback classes with Redis client as attribute


# --- Agent Configuration ---
# Configure and create the main LLM Agent.
def load_agent():
    # Create deep copies of authentication objects to avoid shared references
    auth_scheme_copy = copy.deepcopy(AUTH_SCHEME)
    auth_credential_copy = copy.deepcopy(AUTH_CREDENTIAL)

    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="enterprise_assistant",
        instruction=(
            "Help user integrate with multiple enterprise systems, including retrieving"
            " user information which may require authentication."
        ),
        tools=[connector_tool],
        before_tool_callback=BeforeToolCallback(
            callbacks={
                tool.name: GmailToolBeforeCallback(
                    auth_scheme=auth_scheme_copy, auth_credential=auth_credential_copy
                )
                for tool in connector_tool._tools
            }
        ),
        after_tool_callback=AfterToolCallback(
            callbacks={
                tool.name: GmailToolAfterCallback(
                    auth_scheme=auth_scheme_copy, auth_credential=auth_credential_copy
                )
                for tool in connector_tool._tools
            }
        ),
    )
    return root_agent
