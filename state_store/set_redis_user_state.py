from .redis_state_store import RedisStateStore
from .user_identity import UserIdentity


def set_redis_user_state(user_id: str, provider_name: str, model_name: str, redis_url: str = "redis://localhost:6379/0"):
    try:
        user = UserIdentity(user_id=user_id, provider=provider_name, model=model_name)
        redis_store = RedisStateStore(redis_url=redis_url)
        redis_store.set_state(user)
    except Exception as e:
        raise ValueError(f"Error storing state in Redis: {e}") 