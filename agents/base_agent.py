import json
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger('kidsbook')

# Ensure environment variables from .env are loaded
load_dotenv()

class BaseAgent:
    def __init__(self, config_path: str, agent_key: str):
        """
        Initializes an agent from a JSON configuration file.
        The configuration for the specific agent is loaded from the provided key.
        Azure credentials are injected from environment variables.
        """
        try:
            with open(config_path) as f:
                config_json = json.load(f)
            self.config = config_json.get(agent_key)
            if self.config is None:
                raise KeyError(f"Agent key '{agent_key}' not found in the configuration")
            # Retrieve Azure credentials from environment
            azure_api_key = os.environ.get('AZURE_API_KEY')
            azure_endpoint = os.environ.get('AZURE_ENDPOINT')
            if not azure_api_key or not azure_endpoint:
                raise ValueError("Azure API key and endpoint must be set in the environment")
            self.config['azure_ai'] = {
                'api_key': azure_api_key,
                'endpoint': azure_endpoint
            }
            logger.info(f"Initialized agent '{agent_key}' successfully.")
        except Exception as e:
            logger.exception(f"Error initializing BaseAgent: {str(e)}")
            raise