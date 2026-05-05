import unittest
import requests
from unittest.mock import MagicMock

from code.tools.recordedFuture import (
    RecordedFutureClient,
    BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
)


class TestClientInit(unittest.TestCase):

    def setUp(self):
        self.token_provider = MagicMock(return_value="fake-rf-token")

    def test_defaults(self):
        client = RecordedFutureClient(token_provider=self.token_provider)
        self.assertEqual(client.base_url, BASE_URL)
        self.assertEqual(client.timeout_seconds, DEFAULT_TIMEOUT_SECONDS)
        self.assertIsNotNone(client.session)

    def test_custom_base_url(self):
        client = RecordedFutureClient(
            token_provider=self.token_provider, base_url="https://custom.api"
        )
        self.assertEqual(client.base_url, "https://custom.api")

    def test_custom_timeout(self):
        client = RecordedFutureClient(
            token_provider=self.token_provider, timeout_seconds=30
        )
        self.assertEqual(client.timeout_seconds, 30)

    def test_custom_session_is_used(self):
        custom_session = requests.Session()
        client = RecordedFutureClient(
            token_provider=self.token_provider, session=custom_session
        )
        self.assertIs(client.session, custom_session)

    def test_build_session_mounts_https_adapter(self):
        session = RecordedFutureClient._build_session(max_retries=2, backoff_factor=0.1)
        self.assertIn("https://", session.adapters)

    def test_cached_headers_initially_none(self):
        client = RecordedFutureClient(token_provider=self.token_provider)
        self.assertIsNone(client._cached_headers)


if __name__ == "__main__":
    unittest.main()
