import unittest
import requests
from unittest.mock import MagicMock

from code.tools.recordedFuture import (
    RecordedFutureClient,
    BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
)


class TestPostJson(unittest.TestCase):

    def setUp(self):
        self.token_provider = MagicMock(return_value="fake-rf-token")
        self.client = RecordedFutureClient(token_provider=self.token_provider)

    def _mock_response(self, json_data, status_code=200):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.raise_for_status.return_value = None
        return resp

    def test_successful_post(self):
        expected = {"data": [{"id": 1}]}
        self.client.session.post = MagicMock(
            return_value=self._mock_response(expected)
        )

        result = self.client._post_json("/some/path", {"key": "value"})

        self.assertEqual(result, expected)
        self.client.session.post.assert_called_once_with(
            f"{BASE_URL}/some/path",
            json={"key": "value"},
            headers=self.client._headers(),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

    def test_raises_on_non_dict_response(self):
        self.client.session.post = MagicMock(
            return_value=self._mock_response(["not", "a", "dict"])
        )

        with self.assertRaises(ValueError) as ctx:
            self.client._post_json("/path", {})
        self.assertIn("Expected JSON object", str(ctx.exception))

    def test_raise_for_status_propagates(self):
        resp = MagicMock(spec=requests.Response)
        resp.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        self.client.session.post = MagicMock(return_value=resp)

        with self.assertRaises(requests.HTTPError):
            self.client._post_json("/path", {})

    def test_constructs_correct_url(self):
        self.client.session.post = MagicMock(
            return_value=self._mock_response({"ok": True})
        )
        self.client._post_json("/v1/endpoint", {})

        called_url = self.client.session.post.call_args[0][0]
        self.assertEqual(called_url, f"{BASE_URL}/v1/endpoint")


if __name__ == "__main__":
    unittest.main()
