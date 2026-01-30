from curl_cffi import requests
from utils import check_status_code

from typing import Literal
from ..config import GConfig


class HttpClient:
    def __init__(self, header=None,
                 cookie=None,
                 impersonate=GConfig.global_get("impersonate_browser")):
        self.header = header
        self.cookie = cookie
        self.impersonate = impersonate
        self.timeout = GConfig.global_get("timeout")

    def get_url(self, url: str, mode: Literal["t", "j", "b"] = "t") -> str | dict | bytes:
        r = requests.get(
            url,
            headers=self.header,
            cookies=self.cookie,
            impersonate=self.impersonate,
            timeout=self.timeout
        )
        check_status_code(r.status_code)

        match mode:
            case "t":
                return r.text
            case "j":
                return r.json()
            case "b":
                return r.content

    def post_url(self, url: str, mode: Literal["t", "j", "b"] = "t") -> str | dict | bytes:
        r = requests.post(
            url,
            headers=self.header,
            cookies=self.cookie,
            impersonate=self.impersonate,
            timeout=self.timeout
        )
        check_status_code(r.status_code)

        match mode:
            case "t":
                return r.text
            case "j":
                return r.json()
            case "b":
                return r.content
