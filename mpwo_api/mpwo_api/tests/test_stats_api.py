import json


def test_get_stats_by_time_no_activities(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == {}


def test_get_stats_by_time_no_user(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/1000/by_time',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'User does not exist.' in data['message']


def test_get_stats_by_time_all_activities_error(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from="2018-04-01&to=2018-04-30',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error. Please try again or contact the administrator.' \
           in data['message']


def test_get_stats_by_time_all_activities_invalid_period(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from=2018-04-01&to=2018-04-30&time=day',  # noqa
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'fail' in data['status']
    assert 'Invalid time period.' in data['message']


def test_get_stats_by_time_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2017':
                {
                    '1':
                        {
                            'nb_activities': 2,
                            'total_distance': 15.0,
                            'total_duration': 4480
                        }
                },
            '2018':
                {
                    '1':
                        {
                            'nb_activities': 5,
                            'total_distance': 39.0,
                            'total_duration': 11624
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_time_all_activities_april_2018(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from=2018-04-01&to=2018-04-30',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2018':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_year_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?time=year',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2017':
                {
                    '1':
                        {
                            'nb_activities': 2,
                            'total_distance': 15.0,
                            'total_duration': 4480
                        }
                },
            '2018':
                {
                    '1':
                        {
                            'nb_activities': 5,
                            'total_distance': 39.0,
                            'total_duration': 11624
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_year_all_activities_april_2018(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from=2018-04-01&to=2018-04-30&time=year',  # noqa
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2018':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_month_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?time=month',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2017-03':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 5.0,
                            'total_duration': 1024
                        }
                },
            '2017-06':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 3456
                        }
                },
            '2018-01':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 1024
                        }
                },
            '2018-02':
                {
                    '1':
                        {
                            'nb_activities': 2,
                            'total_distance': 11.0,
                            'total_duration': 1600
                        }
                },
            '2018-04':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                },
            '2018-05':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 3000
                        }
                }
        }


def test_get_stats_by_month_all_activities_april_2018(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from=2018-04-01&to=2018-04-30&time=month',  # noqa
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2018-04':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_week_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?time=week',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2017-W12':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 5.0,
                            'total_duration': 1024
                        }
                },
            '2017-W22':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 3456
                        }
                },
            '2018-W00':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 1024
                        }
                },
            '2018-W13':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                },
            '2018-W07':
                {
                    '1':
                        {
                            'nb_activities': 2,
                            'total_distance': 11.0,
                            'total_duration': 1600
                        }
                },
            '2018-W18':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 3000
                        }
                }
        }


def test_get_stats_by_week_all_activities_week_13(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from=2018-04-01&to=2018-04-30&time=week',  # noqa
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2018-W13':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_weekm_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?time=weekm',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2017-W12':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 5.0,
                            'total_duration': 1024
                        }
                },
            '2017-W22':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 3456
                        }
                },
            '2018-W01':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 1024
                        }
                },
            '2018-W08':
                {
                    '1':
                        {
                            'nb_activities': 2,
                            'total_distance': 11.0,
                            'total_duration': 1600
                        }
                },
            '2018-W13':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                },
            '2018-W19':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 10.0,
                            'total_duration': 3000
                        }
                }
        }


def test_get_stats_by_weekm_all_activities_week_13(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_time?from=2018-04-01&to=2018-04-30&time=weekm',  # noqa
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '2018-W13':
                {
                    '1':
                        {
                            'nb_activities': 1,
                            'total_distance': 8.0,
                            'total_duration': 6000
                        },
                    '2':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_by_sport_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_sport',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '1':
                {
                    'nb_activities': 7,
                    'total_distance': 54.0,
                    'total_duration': 16104
                },
            '2':
                {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000
                }
        }


def test_get_stats_by_sport_all_activities_sport_1(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_sport?sport_id=1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            '1':
                {
                    'nb_activities': 7,
                    'total_distance': 54.0,
                    'total_duration': 16104
                }
        }


def test_get_stats_by_sport_all_activities_invalid_user(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/1000/by_sport?sport_id=1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'User does not exist.' in data['message']


def test_get_stats_by_sport_all_activities_invalid_sport(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_sport?sport_id=999',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'Sport does not exist.' in data['message']


def test_get_stats_by_sport_all_activities_error(
    app, user_1, sport_1_cycling, sport_2_running,
    seven_activities_user_1, activity_running_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        f'/api/stats/{user_1.id}/by_sport?sport_id="999',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error. Please try again or contact the administrator.' \
           in data['message']
