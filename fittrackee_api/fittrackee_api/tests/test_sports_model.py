def assert_sport_model(sport, is_admin=False):
    assert 1 == sport.id
    assert 'Cycling' == sport.label
    assert '<Sport \'Cycling\'>' == str(sport)

    serialized_sport = sport.serialize(is_admin)
    assert 1 == serialized_sport['id']
    assert 'Cycling' == serialized_sport['label']
    assert serialized_sport['is_active'] is True
    return serialized_sport


def test_sport_model(app, sport_1_cycling):
    serialized_sport = assert_sport_model(sport_1_cycling)
    assert 'has_activities' not in serialized_sport


def test_sport_model_with_activity(
    app, sport_1_cycling, user_1, activity_cycling_user_1
):
    serialized_sport = assert_sport_model(sport_1_cycling)
    assert 'has_activities' not in serialized_sport


def test_sport_model_with_activity_admin(
    app, sport_1_cycling, user_1, activity_cycling_user_1
):
    serialized_sport = assert_sport_model(sport_1_cycling, True)
    assert serialized_sport['has_activities'] is True
