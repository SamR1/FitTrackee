from uuid import UUID

from fittrackee.activities.utils_id import decode_short_id


class TestActivityModel:
    def test_activity_model(
        self, app, sport_1_cycling, user_1, activity_cycling_user_1
    ):
        activity_cycling_user_1.title = 'Test'

        assert 1 == activity_cycling_user_1.id
        assert activity_cycling_user_1.uuid is not None
        assert 1 == activity_cycling_user_1.user_id
        assert 1 == activity_cycling_user_1.sport_id
        assert '2018-01-01 00:00:00' == str(
            activity_cycling_user_1.activity_date
        )
        assert 10.0 == float(activity_cycling_user_1.distance)
        assert '1:00:00' == str(activity_cycling_user_1.duration)
        assert 'Test' == activity_cycling_user_1.title
        assert '<Activity \'Cycling\' - 2018-01-01 00:00:00>' == str(
            activity_cycling_user_1
        )

        serialized_activity = activity_cycling_user_1.serialize()
        assert isinstance(decode_short_id(serialized_activity['id']), UUID)
        assert 'test' == serialized_activity['user']
        assert 1 == serialized_activity['sport_id']
        assert serialized_activity['title'] == 'Test'
        assert 'creation_date' in serialized_activity
        assert serialized_activity['modification_date'] is not None
        assert (
            str(serialized_activity['activity_date']) == '2018-01-01 00:00:00'
        )
        assert serialized_activity['duration'] == '1:00:00'
        assert serialized_activity['pauses'] is None
        assert serialized_activity['moving'] == '1:00:00'
        assert serialized_activity['distance'] == 10.0
        assert serialized_activity['max_alt'] is None
        assert serialized_activity['descent'] is None
        assert serialized_activity['ascent'] is None
        assert serialized_activity['max_speed'] == 10.0
        assert serialized_activity['ave_speed'] == 10.0
        assert serialized_activity['with_gpx'] is False
        assert serialized_activity['bounds'] == []
        assert serialized_activity['previous_activity'] is None
        assert serialized_activity['next_activity'] is None
        assert serialized_activity['segments'] == []
        assert serialized_activity['records'] != []
        assert serialized_activity['map'] is None
        assert serialized_activity['weather_start'] is None
        assert serialized_activity['weather_end'] is None
        assert serialized_activity['notes'] is None

    def test_activity_segment_model(
        self,
        app,
        sport_1_cycling,
        user_1,
        activity_cycling_user_1,
        activity_cycling_user_1_segment,
    ):
        assert (
            f'<Segment \'{activity_cycling_user_1_segment.segment_id}\' '
            f'for activity \'{activity_cycling_user_1.short_id}\'>'
            == str(activity_cycling_user_1_segment)
        )
