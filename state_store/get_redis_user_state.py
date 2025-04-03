import logging
import sys
import os
from .redis_state_store import RedisStateStore
from .user_identity import UserIdentity
from .set_redis_user_state import set_redis_user_state

# Set higher logging level for debugging Redis issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_redis_user_state(user_id: str, is_app_home: bool, redis_url: str = None):
    """
    Get user state from Redis
    
    Args:
        user_id: The user ID
        is_app_home: Whether the request is from app home
        redis_url: Optional Redis URL. If not provided, uses REDIS_URL env variable
    
    Returns:
        Tuple of (provider_name, model_name) or (None, None) if not found
    """
    print(f"🔍 Fetching Redis state for user: {user_id}")
    
    # Check if Redis URL is provided or available in environment variables
    if not redis_url:
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            print(f"ℹ️ REDIS_URL not found in environment, Redis storage disabled")
            return None, None
    
    try:
        redis_store = RedisStateStore(redis_url=redis_url)
        user_data = redis_store.get_state(user_id)
        
        if not user_data:
            # Check if GENAI_API_URL is set and use genai-agent as default
            genai_api_url = os.environ.get("GENAI_API_URL")
            if genai_api_url:
                # Set default to genai-agent and save to Redis
                try:
                    print(f"🔄 GENAI_API_URL is set, using genai-agent as default for user: {user_id}")
                    set_redis_user_state(user_id, "genai", "genai-agent", redis_url)
                    print(f"✅ Saved default GenAI selection to Redis for user: {user_id}")
                    return "genai", "genai-agent"
                except Exception as e:
                    error_msg = f"❌ Error saving default GenAI selection: {e}"
                    print(error_msg, file=sys.stderr)
                    logger.error(error_msg)
            
            # If GENAI_API_URL not set or error saving default
            if not is_app_home:
                print(f"ℹ️ No provider selection found for user: {user_id}, using GenAI fallback")
                # Return None, None and let the caller handle the fallback
            print(f"ℹ️ No state found in Redis for user: {user_id}")
            return None, None
        
        user_identity: UserIdentity = user_data
        provider = user_identity.get("provider")
        model = user_identity.get("model")
        
        print(f"✅ Found Redis state for user {user_id}: provider={provider}, model={model}")
        return provider, model
        
    except Exception as e:
        error_msg = f"❌ Error getting Redis state for user {user_id}: {e}"
        print(error_msg, file=sys.stderr)
        logger.error(error_msg)
        return None, None 