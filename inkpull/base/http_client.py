import time
import random

from curl_cffi import requests
from curl_cffi.requests.exceptions import Timeout, HTTPError, ConnectionError as CffiConnectionError

from utils import check_status_code, log

from typing import Literal
from ..config.runtime import GConfig


class HttpClient:
    def __init__(self, headers=None,
                 cookies=None,
                 impersonate=GConfig.global_get("impersonate_browser")):
        self.header = headers
        self.cookie = cookies
        self.impersonate = impersonate
        self.timeout = GConfig.global_get("timeout")
        self.retries = GConfig.global_get("retries")

    def _base(self, url: str,
              mode: Literal["t", "j", "b"] = "t",
              method: Literal["get", "post"] = "get",
              json_payload: dict | None = None,
              params: dict | None = None) -> str | dict | bytes:
        last_error = None

        for i in range(self.retries):
            try:
                match method:
                    case "get":
                        r = requests.get(
                            url,
                            params=params
                        )
                    case "post":
                        r = requests.post(
                            url,
                            timeout=self.timeout,
                            json=json_payload,
                            params=params
                        )
                    case _:
                        raise ValueError(f"Invalid method: {method}")

                check_status_code(r.status_code, url)

                match mode:
                    case "t":
                        return r.text
                    case "j":
                        return r.json()
                    case "b":
                        return r.content

            except (CffiConnectionError, Timeout, HTTPError,) as e:
                last_error = e
                log(f"Retry {i + 1}/{self.retries} failed: {url} -> {e}", level="warn")
                time.sleep((2 ** i) + random.uniform(0, 1))

        raise last_error

    def get_url(self, url: str, mode: Literal["t", "j", "b"] = "t") -> str | dict | bytes:
        return self._base(
            url=url,
            mode=mode,
            method="get"
        )

    def post_url(self, url: str, mode: Literal["t", "j", "b"] = "t",
                 json_payload: dict | None = None) -> str | dict | bytes:
        return self._base(
            url=url,
            mode=mode,
            method="post",
            json_payload=json_payload,
        )
