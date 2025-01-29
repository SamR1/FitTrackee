from unittest.mock import MagicMock, Mock, patch

import pytest

from fittrackee.federation.exceptions import UnsupportedActivityException
from fittrackee.federation.tasks.activity import handle_activity

from ...utils import random_string


class TestHandleActivity:
    def test_it_raises_error_if_activity_not_supported(self) -> None:
        with pytest.raises(UnsupportedActivityException):
            handle_activity(activity={'type': random_string()})

    @patch('fittrackee.federation.tasks.activity.get_activity_instance')
    def test_it_calls_process_activity(
        self, get_activity_instance_mock: Mock
    ) -> None:
        activity_dict = {'type': random_string()}
        activity_mock = MagicMock()
        activity_mock.process_activity = Mock()
        get_activity_instance_mock.return_value = activity_mock

        handle_activity(activity=activity_dict)

        activity_mock.assert_called_with(activity_dict=activity_dict)
        activity_mock().process_activity.assert_called()
