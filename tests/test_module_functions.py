import unittest
from unittest.mock import patch, MagicMock

from code.tools.recordedFuture import (
    searchMalware,
    searchIOC,
    searchSandbox,
    generate_headers,
    _get_recorded_future_token,
)
from code.models.models import MalwareLookupPayload, IOCLookupPayload


class TestSearchMalwareFunction(unittest.TestCase):

    @patch("tools.recordedFuture._client")
    def test_delegates_to_client(self, mock_client):
        payload = MalwareLookupPayload(sha256_list=["abc"])
        searchMalware(payload)
        mock_client.search_malware.assert_called_once_with(payload)


class TestSearchIOCFunction(unittest.TestCase):

    @patch("tools.recordedFuture._client")
    def test_delegates_to_client(self, mock_client):
        payload = IOCLookupPayload(ip=["1.1.1.1"], domain=[], hash=[])
        searchIOC(payload)
        mock_client.search_ioc.assert_called_once_with(payload)


class TestSearchSandboxFunction(unittest.TestCase):

    @patch("tools.recordedFuture._client")
    def test_delegates_to_client(self, mock_client):
        searchSandbox("hash123")
        mock_client.search_sandbox.assert_called_once_with("hash123")


class TestGenerateHeaders(unittest.TestCase):

    @patch("tools.recordedFuture._client")
    def test_delegates_to_client(self, mock_client):
        mock_client._headers.return_value = {"X-RFToken": "tok"}
        result = generate_headers()
        mock_client._headers.assert_called_once()
        self.assertEqual(result, {"X-RFToken": "tok"})


class TestGetRecordedFutureToken(unittest.TestCase):

    @patch("tools.recordedFuture.AWSServices.get_ssm_parameters")
    def test_returns_first_parameter(self, mock_ssm):
        mock_ssm.return_value = ["my-secret-token"]
        token = _get_recorded_future_token()
        self.assertEqual(token, "my-secret-token")
        mock_ssm.assert_called_once_with(["recorded_future_api"], "ap-southeast-2")


if __name__ == "__main__":
    unittest.main()
