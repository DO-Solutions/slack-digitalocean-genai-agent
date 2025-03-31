from .user_state_store import UserStateStore
from .user_identity import UserIdentity
import logging
import json
import redis
import os


class RedisStateStore(UserStateStore):
    def __init__(
        self,
        *,
        redis_url: str = None,
        key_prefix: str = "chatbot:",
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        # Use provided redis_url, or get from environment, or fall back to localhost
        self.redis_url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.Redis.from_url(self.redis_url)
        self.key_prefix = key_prefix
        self.logger = logger

    def set_state(self, user_identity: UserIdentity):
        state = user_identity["user_id"]
        key = f"{self.key_prefix}{state}"
        
        try:
            data = json.dumps(user_identity)
            self.redis_client.set(key, data)
            return state
        except Exception as e:
            self.logger.error(f"Failed to store data for {user_identity} - {e}")
            raise e

    def unset_state(self, user_identity: UserIdentity):
        state = user_identity["user_id"]
        key = f"{self.key_prefix}{state}"
        
        try:
            if self.redis_client.exists(key):
                self.redis_client.delete(key)
                return state
            else:
                raise FileNotFoundError(f"No state found for user {state}")
        except Exception as e:
            self.logger.warning(f"Failed to delete data for {user_identity} - {e}")
            raise e
            
    def get_state(self, user_id: str):
        key = f"{self.key_prefix}{user_id}"
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None 