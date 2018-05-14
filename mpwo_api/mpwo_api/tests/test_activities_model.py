

def test_add_activity(
    app, sport_1_cycling, user_1, activity_cycling_user_1
):
    activity_cycling_user_1.title = 'Test'

    assert 1 == activity_cycling_user_1.id
    assert 1 == activity_cycling_user_1.user_id
    assert 1 == activity_cycling_user_1.sport_id
    assert '2018-01-01 00:00:00' == str(activity_cycling_user_1.activity_date)
    assert 10.0 == float(activity_cycling_user_1.distance)
    assert '0:17:04' == str(activity_cycling_user_1.duration)
    assert 'Test' == activity_cycling_user_1.title
    assert '<Activity \'Cycling\' - 2018-01-01 00:00:00>' == str(activity_cycling_user_1)  # noqa


def test_add_segment(
    app, sport_1_cycling, user_1, activity_cycling_user_1,
    activity_cycling_user_1_segment
):
    assert '<Segment \'0\' for activity \'1\'>' == str(activity_cycling_user_1_segment)  # noqa
