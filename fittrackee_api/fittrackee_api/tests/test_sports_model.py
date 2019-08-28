def test_sport_model(app, sport_1_cycling):
    assert 1 == sport_1_cycling.id
    assert 'Cycling' == sport_1_cycling.label
    assert '<Sport \'Cycling\'>' == str(sport_1_cycling)

    serialized_sport = sport_1_cycling.serialize()
    assert 1 == serialized_sport['id']
    assert 'Cycling' == serialized_sport['label']
    assert serialized_sport['_can_be_deleted'] is True


def test_sport_model_with_activity(
    app, sport_1_cycling, user_1, activity_cycling_user_1
):
    assert 1 == sport_1_cycling.id
    assert 'Cycling' == sport_1_cycling.label
    assert '<Sport \'Cycling\'>' == str(sport_1_cycling)

    serialized_sport = sport_1_cycling.serialize()
    assert 1 == serialized_sport['id']
    assert 'Cycling' == serialized_sport['label']
    assert serialized_sport['_can_be_deleted'] is False
