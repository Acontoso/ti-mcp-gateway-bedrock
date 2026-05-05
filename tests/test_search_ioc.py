import unittest
import requests
from unittest.mock import MagicMock

from code.tools.recordedFuture import RecordedFutureClient
from code.models.models import IOCLookupPayload, IOCSearchResponse


class TestSearchIOC(unittest.TestCase):

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
            "data": {
                "results": [
                    {
                        "risk": {
                            "score": 75,
                            "rule": {
                                "mostCritical": "C2",
                                "count": 3,
                                "maxCount": 10,
                                "evidence": {},
                            },
                        },
                        "entity": {"name": "1.2.3.4", "type": "IpAddress"},
                    }
                ]
            }
        }
        self.client.session.post = MagicMock(
            return_value=self._mock_response(api_data)
        )

        payload = IOCLookupPayload(ip=["1.2.3.4"], domain=[], hash=[])
        result = self.client.search_ioc(payload)

        self.assertIsInstance(result, IOCSearchResponse)
        self.assertEqual(len(result.data.results), 1)
        self.assertEqual(result.data.results[0].risk.score, 75)
        self.assertEqual(result.data.results[0].entity.name, "1.2.3.4")

    def test_empty_results(self):
        api_data = {"data": {"results": []}}
        self.client.session.post = MagicMock(
            return_value=self._mock_response(api_data)
        )

        payload = IOCLookupPayload(ip=[], domain=[], hash=[])
        result = self.client.search_ioc(payload)

        self.assertIsInstance(result, IOCSearchResponse)
        self.assertEqual(result.data.results, [])

    def test_payload_sent_correctly(self):
        self.client.session.post = MagicMock(
            return_value=self._mock_response({"data": {"results": []}})
        )

        payload = IOCLookupPayload(
            ip=["1.2.3.4"], domain=["evil.com"], hash=["abc123"]
        )
        self.client.search_ioc(payload)

        call_kwargs = self.client.session.post.call_args
        sent_payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        self.assertEqual(sent_payload, {
            "ip": ["1.2.3.4"],
            "domain": ["evil.com"],
            "hash": ["abc123"],
        })


if __name__ == "__main__":
    unittest.main()
