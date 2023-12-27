import requests
from typing import Any


class APIClient:
    def __init__(self, server_url: str):
        self.server_url = server_url

    def make_request(self, method: str, endpoint: str, **kwargs):
        response = getattr(requests, method)(f"{self.server_url}/{endpoint}", **kwargs)
        response.raise_for_status()
        return response.json()

    def should_run_scan(self) -> bool:
        return self.make_request('get', 'scan-status').get('should_run', False)

    def fetch_config(self) -> dict:
        return self.make_request('get', 'config')

    def send_data(self, data: Any):
        self.make_request('post', 'data', json=data)

    def signal_scan_completion(self):
        self.make_request('post', 'scan-complete')
