import json
import time
from typing import Any

import requests

from . import config
from .exceptions import FabricError, FabricThrottlingError


def invoke_fabric_api_request(
    uri: str,
    token: str | None = None,
    method: str = "GET",
    body: Any = None,
    content_type: str = "application/json; charset=utf-8",
    timeout_sec: int = 240,
    retry_count: int = 0,
    api_url: str = config.API_URL,
) -> Any:
    headers = {
        "Content-Type": content_type,
        "Authorization": f"Bearer {token}",
    }

    if not api_url:
        raise ValueError("api_url must be specified")

    request_url = f"{api_url.rstrip('/')}/{uri.lstrip('/')}"

    try:
        response = requests.request(
            method=method.upper(),
            url=request_url,
            headers=headers,
            json=body if isinstance(body, (dict, list)) else None,
            data=None if isinstance(body, (dict, list)) else body,
            timeout=timeout_sec,
        )

        # Handle Long-Running Operation (202)
        if response.status_code == 202:
            while True:
                async_url = response.headers.get("Location")
                if not async_url:
                    raise FabricError("LRO response has no Location header")
                print("LRO - Waiting for request to complete in service.")
                time.sleep(5)
                lro_response = requests.get(async_url, headers=headers)
                lro_content = lro_response.json()
                status = lro_content.get("status", "").lower()

                if status in ["succeeded", "failed"]:
                    if status == "succeeded":
                        result_url = lro_response.headers.get("Location")
                        if result_url:
                            response = requests.get(result_url, headers=headers)
                        else:
                            return None  # LRO has no result body
                    else:
                        error = lro_content.get("error", {})
                        raise FabricError(
                            f"LRO failed: {error.get('errorCode')} - {error.get('message')}"
                        )
                    break

        # Parse JSON response
        if response.content:
            content_bytes = response.content
            content_text = (
                content_bytes[3:].decode("utf-8")
                if content_bytes.startswith(b"\xef\xbb\xbf")
                else response.text
            )
            json_result = json.loads(content_text)

            if isinstance(json_result, dict) and "errorCode" in json_result:
                raise FabricError(
                    f"API Error: {json_result['errorCode']} - {json_result.get('message')}"
                )

            if isinstance(json_result, dict) and "value" in json_result:
                return json_result["value"]

            return json_result

    except requests.exceptions.RequestException as ex:
        raw_response = getattr(ex, "response", None)

        if raw_response is not None and raw_response.status_code == 429:
            retry_after = raw_response.headers.get("Retry-After")
            wait = int(retry_after) + 5 if retry_after and retry_after.isdigit() else 60
            print(f"Too many requests (429). Sleeping {wait}s.")
            time.sleep(wait)
            if retry_count < 3:
                return invoke_fabric_api_request(
                    uri=uri,
                    token=token,
                    method=method,
                    body=body,
                    content_type=content_type,
                    timeout_sec=timeout_sec,
                    retry_count=retry_count + 1,
                    api_url=api_url,
                )
            raise FabricThrottlingError("Exceeded max retries after 429 Too Many Requests")

        raise FabricError(str(ex))
