import unittest
from lib.adapters.redis_adapter import RedisAdapter

class TestRedisAdapter(unittest.TestCase):
    """test class for Redis adapter"""
    def setUp(self):
        """setup"""
        self.adapter = RedisAdapter(host='localhost', port=6379, db=0, password=None)

    def test_redis_adapter_initialization(self):
        """test init"""
        self.assertIsNotNone(self.adapter.redis_client)