import os
from atproto import Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class BlueskyAuth:
    def __init__(self):
        load_dotenv()
        self.handle = os.getenv("BLUESKY_HANDLE")
        self.password = os.getenv("BLUESKY_PASSWORD")
        self.client = None

    def login(self) -> Client:
        """Login to Bluesky and return authenticated client"""
        if not self.handle or not self.password:
            raise ValueError("Bluesky credentials not found in .env file")

        try:
            self.client = Client()
            self.client.login(self.handle, self.password)
            logger.info(f"Successfully logged in as {self.handle}")
            return self.client
        except Exception as e:
            logger.error(f"Failed to login: {e}")
            raise

    def get_client(self) -> Client:
        """Get authenticated client, login if necessary"""
        if self.client is None:
            self.login()
        return self.client
