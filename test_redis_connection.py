# test_redis_connection.py
import redis

def test_redis():
    try:
        r = redis.StrictRedis(host='redis', port=6379, db=0)
        r.ping()
        print("Redis connection successful")
    except Exception as e:
        print(f"Redis connection failed: {e}")

test_redis()

