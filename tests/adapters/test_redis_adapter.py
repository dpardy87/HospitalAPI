import unittest
from unittest.mock import MagicMock, patch
from lib.adapters.redis_adapter import RedisAdapter


class TestRedisAdapter(unittest.TestCase):
    """test class for Redis adapter"""

    def setUp(self):
        """setup"""
        self.adapter = RedisAdapter(host="localhost", port=6379, db=0, password=None)
        self.adapter.redis_client = MagicMock()

    @patch("lib.adapters.redis_adapter.redis.Redis")
    def test_initialization(self, mock_redis):
        """Test that RedisAdapter initializes correctly"""
        mock_redis.return_value = MagicMock()
        adapter = RedisAdapter(host="localhost", port=6379, db=0, password=None)
        mock_redis.assert_called_once_with(
            host="localhost", port=6379, db=0, password=None
        )
        self.assertIsNotNone(adapter.redis_client)

    def test_get_single_key(self):
        """Test retrieving a single key"""
        self.adapter.redis_client.get.return_value = b"zebras are neat!"
        result = self.adapter.get("a_very_important_key")
        self.adapter.redis_client.get.assert_called_once_with("a_very_important_key")
        self.assertEqual(result, "zebras are neat!")
