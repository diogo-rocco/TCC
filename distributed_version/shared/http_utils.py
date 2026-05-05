import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session(timeout: int = 10, total_retries: int = 5, backoff: float = 0.5) -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=total_retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "HEAD", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.request_timeout = timeout
    return session

SESSION = make_session()
