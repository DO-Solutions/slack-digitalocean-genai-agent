import logging
from .redis_state_store import RedisStateStore
from .user_identity import UserIdentity

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def get_redis_user_state(user_id: str, is_app_home: bool, redis_url: str = "redis://localhost:6379/0"):
    redis_store = RedisStateStore(redis_url=redis_url)
    user_data = redis_store.get_state(user_id)
    
    if not is_app_home and not user_data:
        raise FileNotFoundError("No provider selection found. Please navigate to the App Home and make a selection.")
    
    try:
        if user_data:
            user_identity: UserIdentity = user_data
            return user_identity["provider"], user_identity["model"]
        return None, None
    except Exception as e:
        logger.error(e)
        raise e 