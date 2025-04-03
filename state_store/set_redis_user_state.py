import logging
import sys
import os
from .redis_state_store import RedisStateStore
from .user_identity import UserIdentity

# Set higher logging level for debugging Redis issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_redis_user_state(user_id: str, provider_name: str, model_name: str, redis_url: str = None):
    """
    Set user state in Redis
    
    Args:
        user_id: The user ID
        provider_name: The provider name
        model_name: The model name
        redis_url: Optional Redis URL. If not provided, uses REDIS_URL env variable
    """
    print(f"💾 Setting Redis state for user {user_id}: provider={provider_name}, model={model_name}")
    
    # Check if Redis URL is provided or available in environment variables
    if not redis_url:
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            print(f"ℹ️ REDIS_URL not found in environment, Redis storage disabled")
            return
    
    try:
        user = UserIdentity(user_id=user_id, provider=provider_name, model=model_name)
        redis_store = RedisStateStore(redis_url=redis_url)
        redis_store.set_state(user)
        print(f"✅ Successfully saved Redis state for user {user_id}")
    except Exception as e:
        error_msg = f"❌ Error storing state in Redis for user {user_id}: {e}"
        print(error_msg, file=sys.stderr)
        logger.error(error_msg)
        # Don't raise the error, just log it
        # This allows the application to continue without Redis 