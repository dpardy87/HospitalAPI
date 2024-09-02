"""Redis adapter"""

import redis


class RedisAdapter:
    """redis adapter class"""

    def __init__(self, host, port=6379, db=0, password=None, logger=None):
        """set client attrs"""
        self.redis_client = redis.Redis(host=host, port=port, db=db, password=password)
        self.logger = logger

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
            self.logger.error("Redis get error: %s", str(e))
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
            self.logger.error("Redis keys error: %s", str(e))
            return []

    def set(self, key, value, ex=None):
        """Set a value with optional expiration time"""
        try:
            self.redis_client.set(key, value, ex=ex)
            return True
        except redis.RedisError as e:
            self.logger.error("Redis set error: %s", str(e))
            return False

    def delete_all_keys(self):
        """delete all kv pairs"""
        try:
            keys = self.redis_client.keys("*")
            if keys:
                self.redis_client.delete(*keys)
            self.logger.info(f"Deleted {len(keys)} keys.")
        except Exception as e:
            self.logger.error(f"An error occurred while deleting keys: {str(e)}")
