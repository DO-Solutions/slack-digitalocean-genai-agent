from .user_state_store import UserStateStore
from .user_identity import UserIdentity
import logging
import json
import redis
import os
import sys


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
        self.logger = logger
        self.key_prefix = key_prefix
        
        try:
            print(f"🔌 Connecting to Redis at {self.redis_url[:self.redis_url.index('@') if '@' in self.redis_url else len(self.redis_url)]}")
            # Set decode_responses=True to automatically decode bytes to strings
            self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            # Verify connection by pinging Redis
            if not self.redis_client.ping():
                error_msg = f"❌ Failed to connect to Redis at {self.redis_url[:self.redis_url.index('@') if '@' in self.redis_url else len(self.redis_url)]}"
                print(error_msg, file=sys.stderr)
                self.logger.error(error_msg)
            else:
                print(f"✅ Successfully connected to Redis")
        except Exception as e:
            error_msg = f"❌ Error connecting to Redis: {e}"
            print(error_msg, file=sys.stderr)
            self.logger.error(f"Error connecting to Redis at {self.redis_url}: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def set_state(self, user_identity: UserIdentity):
        state = user_identity["user_id"]
        key = f"{self.key_prefix}{state}"
        
        try:
            data = json.dumps(user_identity)
            result = self.redis_client.set(key, data)
            if result:
                print(f"✅ Redis: Successfully stored state for user {state}")
                self.logger.info(f"Successfully stored state for user {state} at key {key}")
            else:
                error_msg = f"❌ Redis: Set operation failed for key {key}"
                print(error_msg, file=sys.stderr)
                self.logger.error(error_msg)
            return state
        except Exception as e:
            error_msg = f"❌ Redis: Error storing data for user {state}: {e}"
            print(error_msg, file=sys.stderr)
            self.logger.error(f"Failed to store data for {user_identity} at key {key}: {e}")
            raise e

    def unset_state(self, user_identity: UserIdentity):
        state = user_identity["user_id"]
        key = f"{self.key_prefix}{state}"
        
        try:
            if self.redis_client.exists(key):
                self.redis_client.delete(key)
                print(f"✅ Redis: Deleted state for user {state}")
                self.logger.info(f"Deleted state for user {state} at key {key}")
                return state
            else:
                error_msg = f"⚠️ Redis: No state found for user {state}"
                print(error_msg)
                self.logger.warning(f"No state found for user {state} at key {key}")
                raise FileNotFoundError(f"No state found for user {state}")
        except Exception as e:
            error_msg = f"❌ Redis: Error deleting data for user {state}: {e}"
            print(error_msg, file=sys.stderr)
            self.logger.warning(f"Failed to delete data for {user_identity} at key {key}: {e}")
            raise e
            
    def get_state(self, user_id: str):
        key = f"{self.key_prefix}{user_id}"
        
        try:
            data = self.redis_client.get(key)
            if data:
                print(f"✅ Redis: Retrieved state for user {user_id}")
                self.logger.info(f"Retrieved state for user {user_id} from key {key}")
                return json.loads(data)
            else:
                print(f"⚠️ Redis: No state found for user {user_id}")
                self.logger.info(f"No state found for user {user_id} at key {key}")
                return None
        except Exception as e:
            error_msg = f"❌ Redis: Error retrieving state for user {user_id}: {e}"
            print(error_msg, file=sys.stderr)
            self.logger.error(f"Error retrieving state for user {user_id} from key {key}: {e}")
            return None 