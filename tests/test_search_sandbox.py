import unittest
import requests
from unittest.mock import MagicMock

from code.tools.recordedFuture import RecordedFutureClient
from code.models.models import MalwareAnalysisResponse


class TestSearchSandbox(unittest.TestCase):

    def setUp(self):
        self.token_provider = MagicMock(return_value="fake-rf-token")
        self.client = RecordedFutureClient(token_provider=self.token_provider)

    def _mock_response(self, json_data):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = 200
        resp.json.return_value = json_data
        resp.raise_for_status.return_value = None
        return resp

    def test_returns_validated_response(self):
        api_data = {
            "reports": [
                {
                    "file": "malware.exe",
                    "sample": {
                        "id": "sample-1",
                        "score": 100,
                        "tags": ["ransomware"],
                    },
                    "dynamic": {
                        "signatures_count": 5,
                        "signatures": [
                            {"name": "anti-vm", "desc": "Detects VM", "label": "evasion"}
                        ],
                    },
                }
            ]
        }
        self.client.session.post = MagicMock(
            return_value=self._mock_response(api_data)
        )

        result = self.client.search_sandbox("deadbeefhash")

        self.assertIsInstance(result, MalwareAnalysisResponse)
        self.assertEqual(len(result.reports), 1)
        self.assertEqual(result.reports[0].file, "malware.exe")
        self.assertEqual(result.reports[0].dynamic.signatures_count, 5)

    def test_payload_sent_correctly(self):
        self.client.session.post = MagicMock(
            return_value=self._mock_response({"reports": []})
        )

        self.client.search_sandbox("somehash")

        call_kwargs = self.client.session.post.call_args
        sent_payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        self.assertEqual(sent_payload, {
            "query": "dynamic.signatures_count > 1",
            "sha256": "somehash",
            "start_date": "2023-11-01",
        })

    def test_empty_reports(self):
        self.client.session.post = MagicMock(
            return_value=self._mock_response({"reports": []})
        )

        result = self.client.search_sandbox("hash123")

        self.assertIsInstance(result, MalwareAnalysisResponse)
        self.assertEqual(result.reports, [])


if __name__ == "__main__":
    unittest.main()
