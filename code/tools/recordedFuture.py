import requests
from requests.adapters import HTTPAdapter
from typing import Any, Callable
from urllib3.util.retry import Retry
from models.models import (
    MalwareAnalysisResponse,
    MalwareLookupPayload,
    MalwareLookupResponse,
    IOCLookupPayload,
    IOCSearchResponse,
)
from services.aws import AWSServices

BASE_URL = "https://api.recordedfuture.com"
DEFAULT_REGION = "ap-southeast-2"
DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
_RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


class RecordedFutureClient:
    """Typed client for Recorded Future APIs with shared HTTP/session concerns."""

    def __init__(
        self,
        token_provider: Callable[[], str], #passing in a function as an argument - pointer
        base_url: str = BASE_URL,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.token_provider = token_provider
        # Creates a session object that can be reused across multiple requests, improving performance by reusing underlying TCP connections. If no session is provided, it initializes a new one.
        # Ideal for calls to a single API endpoint (like Recorded Future) where connection reuse can reduce latency and resource usage.
        # Each request will share cookies, headers, authentication & connection pool
        self.session = session or self._build_session(max_retries, backoff_factor)
        self._cached_headers: dict[str, str] | None = None

    @staticmethod
    def _build_session(max_retries: int, backoff_factor: float) -> requests.Session:
        # Retry on transient server/network errors with exponential backoff.
        # backoff_factor controls sleep between retries: {backoff_factor} * (2 ** (attempt - 1)).
        # e.g. with backoff_factor=0.5: 0.5 s, 1 s, 2 s between retries.
        retry = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=_RETRY_STATUS_CODES,
            allowed_methods={"POST"},
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        # Adapter handles connection pooling and retry logic for HTTP requests. By mounting it to "https://", all HTTPS requests made through this session will use the retry logic defined above.
        session = requests.Session()
        session.mount("https://", adapter)
        return session

    def _headers(self) -> dict[str, str]:
        # caches the RF token header once per Lambda runtime instance.
        # Warm instances can reuse the cached header, while cold starts will fetch the token and cache it for subsequent calls.
        if self._cached_headers is None:
            self._cached_headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "X-RFToken": self.token_provider(),
            }
        return self._cached_headers

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = self.session.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object response from Recorded Future API")
        return data

    def search_malware(
        self, event: MalwareLookupPayload
    ) -> list[MalwareLookupResponse]:
        payload = {
            "field": "sha256",
            "sha256_list": event.sha256_list,
            "start_date": "2023-11-01",
        }
        json_response = self._post_json("/malware-intelligence/v1/query_iocs", payload)
        data = json_response.get("data", [])
        if not data:
            return [MalwareLookupResponse(risk_score=0, file_extensions=[], tags=[])]

        data_return: list[MalwareLookupResponse] = []
        for item in data:
            risk_score = item.get("risk_score", 0)
            file_extensions = item.get("file_extensions", [])
            tags = item.get("tags", [])
            sandbox_score = item.get("sandbox_score", 0)
            data_return.append(
                MalwareLookupResponse(
                    risk_score=risk_score,
                    file_extensions=file_extensions,
                    tags=tags,
                    sandbox_score=sandbox_score,
                    hash=item.get("name"),
                )
            )
        return data_return

    def search_ioc(self, event: IOCLookupPayload) -> IOCSearchResponse:
        payload = {
            "ip": event.ip or [],
            "domain": event.domain or [],
            "hash": event.hash or [],
        }
        json_response = self._post_json("/soar/v3/enrichment", payload)
        return IOCSearchResponse.model_validate(json_response)

    def search_sandbox(self, hash_value: str) -> MalwareAnalysisResponse:
        payload = {
            "query": "dynamic.signatures_count > 1",
            "sha256": hash_value,
            "start_date": "2023-11-01",
        }
        json_response = self._post_json("/malware-intelligence/v1/reports", payload)
        return MalwareAnalysisResponse.model_validate(json_response)


def _get_recorded_future_token() -> str:
    return AWSServices.get_ssm_parameters(["apikey"], DEFAULT_REGION)[0]


_client = RecordedFutureClient(token_provider=_get_recorded_future_token)


def generate_headers():
    """Build HTTP headers required for all Recorded Future API requests"""
    return _client._headers()


def searchMalware(event: MalwareLookupPayload) -> list[MalwareLookupResponse]:
    """Query malware intelligence for one or more SHA256 file hashes.

    This function calls Recorded Future's malware IOC endpoint and returns a
    normalized list of malware attributes per matched hash.

    When to call:
    - Use this MCP tool when you need malware metadata for known sample hashes
      (for example: triage enrichment, scoring, tagging, extension profiling).
    - Call when the input data is specifically SHA256 values, not generic IOC
      types like IP/domain.

    Arguments:
    - event (MalwareLookupPayload): Pydantic payload containing:
      - `sha256_list` (List[str]): One or more SHA256 hashes to query.

    Returns:
    - list[MalwareLookupResponse]: A list where each item includes:
      - `risk_score` (int)
      - `file_extensions` (List[str])
      - `tags` (List[str])
      - `sandbox_score` (Optional[int])
      - `hash` (str)
    """
    return _client.search_malware(event)


def searchIOC(event: IOCLookupPayload) -> IOCSearchResponse:
    """Perform multi-type IOC enrichment for hashes, domains, and IP addresses.

    This function calls Recorded Future's SOAR enrichment endpoint and validates
    the response into the typed `IOCSearchResponse` model.

    When to call:
    - Use this MCP tool for general IOC enrichment workflows where inputs may
      include one or more IOC types (IP, domain, hash) in a single request.
    - Prefer this over `searchMalware` when you need broad IOC risk context
      rather than malware-sample-specific metadata.

    Arguments:
    - event (IOCLookupPayload): Pydantic payload containing:
      - `hash` (List[str]): File hashes.
      - `domain` (List[str]): Domain names.
      - `ip` (List[str]): IPv4/IPv6 addresses.

    Returns:
    - IOCSearchResponse: Parsed response containing IOC enrichment results under
      `data.results`, including entity and risk information.
    """
    return _client.search_ioc(event)


def searchSandbox(hash: str) -> MalwareAnalysisResponse:
    """Retrieve malware dynamic-analysis (sandbox) reports for a SHA256 hash.

    This function queries malware sandbox reports and returns behavioral analysis
    data such as signatures, network activity, processes, and extracted artifacts.

    When to call:
    - Use this MCP tool after hash triage when detailed behavioral evidence is
      needed (for example: incident investigation or malware detonation context).
    - Call when you specifically need sandbox report content, not just IOC risk
      scoring.

    Arguments:
    - hash (str): SHA256 hash of the malware sample to search.

    Returns:
    - MalwareAnalysisResponse: Parsed malware report object, typically including
      `reports[]` entries with `sample` and `dynamic` analysis details.
    """
    return _client.search_sandbox(hash)
