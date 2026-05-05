import unittest
from unittest.mock import MagicMock

from code.tools.recordedFuture import RecordedFutureClient


class TestHeaders(unittest.TestCase):

    def setUp(self):
        self.token_provider = MagicMock(return_value="fake-rf-token")
        self.client = RecordedFutureClient(token_provider=self.token_provider)

    def test_headers_contain_token(self):
        headers = self.client._headers()
        self.assertEqual(headers["X-RFToken"], "fake-rf-token")

    def test_headers_contain_accept(self):
        headers = self.client._headers()
        self.assertEqual(headers["accept"], "application/json")

    def test_headers_contain_content_type(self):
        headers = self.client._headers()
        self.assertEqual(headers["content-type"], "application/json")

    def test_headers_cached_after_first_call(self):
        first = self.client._headers()
        second = self.client._headers()
        self.assertIs(first, second)

    def test_token_provider_called_once(self):
        self.client._headers()
        self.client._headers()
        self.token_provider.assert_called_once()


if __name__ == "__main__":
    unittest.main()
