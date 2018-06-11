def test_user_model(app, user_1):
    assert '<User \'test\'>' == str(user_1)

    serialized_user = user_1.serialize()
    assert 1 == serialized_user['id']
    assert 'test' == serialized_user['username']
    assert 'created_at' in serialized_user
    assert serialized_user['admin'] is False
    assert serialized_user['first_name'] is None
    assert serialized_user['last_name'] is None
    assert serialized_user['bio'] is None
    assert serialized_user['location'] is None
    assert serialized_user['birth_date'] is None
    assert serialized_user['picture'] is False
    assert serialized_user['timezone'] is None
    assert serialized_user['nb_activities'] == 0
    assert serialized_user['nb_sports'] == 0
    assert serialized_user['total_distance'] == 0
    assert serialized_user['total_duration'] == '0:00:00'
