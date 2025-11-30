import logging
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from vyper import v

# HACK: Disable IPv6 to avoid issues in certain environments.
requests.packages.urllib3.util.connection.HAS_IPV6 = False

PROJECT_ROOT = Path(__file__).resolve().parent


@pytest.fixture(scope="session", autouse=True)
def load_env_vars():
    """Load environment variables from a .env file if it exists."""
    env_path = PROJECT_ROOT / ".env.test"
    load_dotenv(dotenv_path=env_path)
    logging.info(f"Loaded environment variables from {env_path}")


@pytest.fixture(scope="session", autouse=True)
def load_vyper_config():
    """
    Loads configuration files from paths.

    Returns
    -------

    """
    config_path = PROJECT_ROOT

    v.set_env_key_replacer(".", "_")

    v.set_config_type("yaml")
    v.set_config_name("config_test")

    v.add_config_path(config_path)

    try:
        v.read_in_config()
        logging.info("Configuration loaded from %s", config_path)
    except Exception as e:
        logging.warning("no configuration files found: %s", e)
        raise Exception("No configuration files found") from e

    v.automatic_env()
