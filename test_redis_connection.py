import logging
import os
import redis
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_redis_connection():
    # Get Redis URL from environment
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        logger.error("REDIS_URL environment variable not set")
        return False
    
    logger.info(f"Testing connection to Redis at {redis_url}")
    
    try:
        # Connect to Redis
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        if client.ping():
            logger.info("✅ Successfully connected to Redis")
        else:
            logger.error("❌ Redis ping failed")
            return False
            
        # Test write operation
        test_key = "test:connection"
        test_value = {"test": "value", "timestamp": "now"}
        
        result = client.set(test_key, json.dumps(test_value))
        if result:
            logger.info(f"✅ Successfully wrote test data to Redis key '{test_key}'")
        else:
            logger.error(f"❌ Failed to write test data to Redis key '{test_key}'")
            return False
            
        # Test read operation
        data = client.get(test_key)
        if data:
            logger.info(f"✅ Successfully read test data from Redis: {data}")
        else:
            logger.error(f"❌ Failed to read test data from Redis")
            return False
            
        # Clean up
        client.delete(test_key)
        logger.info(f"✅ Successfully cleaned up test data")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Redis connection: {e}")
        return False

if __name__ == "__main__":
    success = test_redis_connection()
    if success:
        print("\n✅ All Redis connection tests passed! Your Redis connection is working correctly.")
    else:
        print("\n❌ Redis connection test failed. See logs above for details.") 