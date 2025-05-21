# utilities/discovery.py
# =============================================================================
# 🎯 Purpose:
# A shared utility module for discovering Agent-to-Agent (A2A) servers.
# It reads a registry of agent base URLs (from a JSON file) and fetches
# each agent's metadata (AgentCard) from the standard discovery endpoint.
# This allows any client or agent to dynamically learn about available agents.
# =============================================================================

import os                            # os provides functions for interacting with the operating system, such as file paths
import json                          # json allows encoding and decoding JSON data
import logging                       # logging is used to record warning/error/info messages
from typing import List             # List is a type hint for functions that return lists

import httpx                         # httpx is an async HTTP client library for sending requests
from models.agent import AgentCard   # AgentCard is a Pydantic model representing an agent's metadata

# Create a named logger for this module; __name__ is the module's name
logger = logging.getLogger(__name__)


class DiscoveryClient:
    """
    🔍 Discovers A2A agents by reading a registry file of URLs and querying
    each one's /.well-known/agent.json endpoint to retrieve an AgentCard.

    Attributes:
        registry_file (str): Path to the JSON file listing base URLs (strings).
        base_urls (List[str]): Loaded list of agent base URLs.
    """

    def __init__(self, registry_file: str = None):
        """
        Initialize the DiscoveryClient.

        Args:
            registry_file (str, optional): Path to the registry JSON. If None,
                defaults to 'agent_registry.json' in this utilities folder.
        """
        # If the caller provided a custom path, use it; otherwise, build the default path
        if registry_file:
            self.registry_file = registry_file
        else:
            # __file__ is this module's file; dirname gets the folder containing it
            # join constructs a path to 'agent_registry.json' alongside this script
            self.registry_file = os.path.join(
                os.path.dirname(__file__),
                "agent_registry.json"
            )

        # Immediately load the registry file into memory
        self.base_urls = self._load_registry()

    def _load_registry(self) -> List[str]:
        """
        Load and parse the registry JSON file into a list of URLs.

        Returns:
            List[str]: The list of agent base URLs, or empty list on error.
        """
        try:
            # Open the file at self.registry_file in read mode
            with open(self.registry_file, "r") as f:
                # Parse the entire file as JSON
                data = json.load(f)
            # Ensure the JSON is a list, not an object or other type
            if not isinstance(data, list):
                raise ValueError("Registry file must contain a JSON list of URLs.")
            return data
        except FileNotFoundError:
            # If the file doesn't exist, log a warning and return an empty list
            logger.warning(f"Registry file not found: {self.registry_file}")
            return []
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON is invalid or wrong type, log an error and return empty list
            logger.error(f"Error parsing registry file: {e}")
            return []

    async def list_agent_cards(self) -> dict:
        """
        Asynchronously fetch the discovery endpoint from each registered URL
        and parse the returned JSON into a dict of {agent_id: AgentCard}.
        """
        cards = {}
        async with httpx.AsyncClient() as client:
            for base in self.base_urls:
                url = base.rstrip("/") + "/.well-known/agent.json"
                try:
                    response = await client.get(url, timeout=5.0)
                    response.raise_for_status()
                    data = response.json()
                    # dict 구조 (멀티 agent 표준)
                    if isinstance(data, dict):
                        for agent_id, card_dict in data.items():
                            card = AgentCard.model_validate(card_dict)
                            cards[agent_id] = card
                    # list 구조 (기존 단일 agent)
                    elif isinstance(data, list):
                        for card_dict in data:
                            card = AgentCard.model_validate(card_dict)
                            cards[card.name] = card  # fallback: name 사용
                except Exception as e:
                    logger.warning(f"Failed to discover agent at {url}: {e}")
        return cards
