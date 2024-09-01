"""reusable Redis adapter class"""

import redis


class RedisAdapter:
    """RedisAdapter"""

    def __init__(self, host, port=6379, db=0, password=None):
        """set client attrs"""
        self.redis_client = redis.Redis(host=host, port=port, db=db, password=password)

    def get(self, *keys):
        """get values via key(s)"""
        try:

            if len(keys) == 1:
                # if only one key, decode val and return
                value = self.redis_client.get(keys[0])
                return value.decode("utf-8") if value else None
            # otherwise use mget and list comp
            values = self.redis_client.mget(keys)
            return [value.decode("utf-8") if value else None for value in values]
        except redis.RedisError as e:
            print(f"Redis get error: {e}")
            return None if len(keys) == 1 else [None] * len(keys)

    def keys(self, pattern):
        """get all values for keys matching a specific pattern"""
        try:
            # get keys matching pattern
            matching_keys = self.redis_client.keys(pattern)

            # mget to get the values
            values = self.redis_client.mget(matching_keys)

            # list comp
            return [value.decode("utf-8") if value else None for value in values]
        except redis.RedisError as e:
            print(f"Redis keys error: {e}")
            return []

    def set(self, key, value, ex=None):
        """set a value w optional expiration time"""
        try:
            self.redis_client.set(key, value, ex=ex)
            return True
        except redis.RedisError as e:
            print(f"Redis set error: {e}")
            return False

    def delete_all_keys(self):
        """delete all kv pairs"""
        try:
            keys = self.redis_client.keys("*")
            if keys:
                self.redis_client.delete(*keys)
            return f"Deleted {len(keys)} keys."
        except redis.exceptions.ConnectionError:
            return (
                "Failed to connect to Redis. Please check your Redis server connection."
            )
        except redis.exceptions.TimeoutError:
            return "The request to Redis timed out. Please try again later."
        except redis.exceptions.ResponseError as e:
            return f"Redis responded with an error: {str(e)}"
        except redis.exceptions.RedisError as e:
            return f"An unexpected Redis error occurred: {str(e)}"
