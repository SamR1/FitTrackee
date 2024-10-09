import pytest

from ..mixins import ApiTestCaseMixin


@pytest.mark.disable_autouse_update_records_patch
class WorkoutApiTestCaseMixin(ApiTestCaseMixin):
    pass
