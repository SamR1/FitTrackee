import json
import re
from typing import Dict, Optional

from werkzeug.test import TestResponse


def assert_errored_response(
    response: TestResponse,
    status_code: int,
    error_message: Optional[str] = None,
    status: Optional[str] = "error",
    match: Optional[str] = None,
) -> Dict:
    assert response.content_type == "application/json"
    assert response.status_code == status_code

    data = json.loads(response.data.decode())
    assert status in data["status"]
    if error_message is not None:
        assert error_message in data["message"]
    if match is not None:
        assert re.match(match, data["message"])
    return data


def assert_oauth_errored_response(
    response: TestResponse,
    status_code: int,
    error: str,
    error_description: Optional[str] = None,
) -> Dict:
    assert response.content_type == "application/json"
    assert response.status_code == status_code

    data = json.loads(response.data.decode())
    assert error in data["error"]
    if error_description is not None:
        assert error_description in data["error_description"]
    return data
