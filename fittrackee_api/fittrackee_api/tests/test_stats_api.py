import json


class TestGetStatsByTime:
    def test_it_gets_no_stats_when_user_has_no_activities(self, app, user_1):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {}

    def test_it_returns_error_when_user_does_not_exists(self, app, user_1):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/stats/1000/by_time',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'User does not exist.' in data['message']

    def test_it_returns_error_if_date_format_is_invalid(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from="2018-04-01&to=2018-04-30',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'Error. Please try again or contact the administrator.'
            in data['message']
        )

    def test_it_returns_error_if_period_is_invalid(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from=2018-04-01&to=2018-04-30&time=day',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'fail' in data['status']
        assert 'Invalid time period.' in data['message']

    def test_it_gets_stats_by_time_all_activities(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017': {
                '1': {
                    'nb_activities': 2,
                    'total_distance': 15.0,
                    'total_duration': 4480,
                }
            },
            '2018': {
                '1': {
                    'nb_activities': 5,
                    'total_distance': 39.0,
                    'total_duration': 11624,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            },
        }

    def test_it_gets_stats_for_april_2018(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from=2018-04-01&to=2018-04-30',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }

    def test_it_gets_stats_for_april_2018_with_paris_timezone(
        self,
        app,
        user_1_paris,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1_paris.username}/by_time?'
            f'from=2018-04-01&to=2018-04-30',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }

    def test_it_gets_stats_by_year(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=year',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017': {
                '1': {
                    'nb_activities': 2,
                    'total_distance': 15.0,
                    'total_duration': 4480,
                }
            },
            '2018': {
                '1': {
                    'nb_activities': 5,
                    'total_distance': 39.0,
                    'total_duration': 11624,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            },
        }

    def test_it_gets_stats_by_year_for_april_2018(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from=2018-04-01&to=2018-04-30&time=year',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }

    def test_it_gets_stats_by_year_for_april_2018_with_paris_timezone(
        self,
        app,
        user_1_paris,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1_paris.username}/by_time?from=2018-04-01&to=2018-04-30&time=year',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }

    def test_it_gets_stats_by_month(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=month',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                }
            },
            '2017-06': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                }
            },
            '2018-01': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                }
            },
            '2018-02': {
                '1': {
                    'nb_activities': 2,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                }
            },
            '2018-04': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            },
            '2018-05': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                }
            },
        }

    def test_it_gets_stats_by_month_with_new_york_timezone(
        self,
        app,
        user_1_full,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1_full.username}/by_time?time=month',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                }
            },
            '2017-06': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                }
            },
            '2018-01': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                }
            },
            '2018-02': {
                '1': {
                    'nb_activities': 2,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                }
            },
            '2018-04': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            },
            '2018-05': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                }
            },
        }

    def test_it_gets_stats_by_month_for_april_2018(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from=2018-04-01&to=2018-04-30&time=month',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018-04': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }

    def test_it_gets_stats_by_week(
        self,
        app,
        user_1_full,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1_full.username}/by_time?time=week',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03-19': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                }
            },
            '2017-05-28': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                }
            },
            '2017-12-31': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                }
            },
            '2018-02-18': {
                '1': {
                    'nb_activities': 2,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                }
            },
            '2018-04-01': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            },
            '2018-05-06': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                }
            },
        }

    def test_it_gets_stats_by_week_for_week_13(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from=2018-04-01&to=2018-04-30&time=week',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018-04-01': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }

    def test_if_get_stats_by_week_starting_with_monday(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=weekm',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03-20': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                }
            },
            '2017-05-29': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                }
            },
            '2018-01-01': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                }
            },
            '2018-02-19': {
                '1': {
                    'nb_activities': 2,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                }
            },
            '2018-03-26': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            },
            '2018-05-07': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                }
            },
        }

    def test_it_gets_stats_by_week_starting_with_monday_for_week_13(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?from=2018-04-01&to=2018-04-30&time=weekm',  # noqa
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018-03-26': {
                '1': {
                    'nb_activities': 1,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                },
                '2': {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                },
            }
        }


class TestGetStatsBySport:
    def test_it_gets_stats_by_sport(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '1': {
                'nb_activities': 7,
                'total_distance': 54.0,
                'total_duration': 16104,
            },
            '2': {
                'nb_activities': 1,
                'total_distance': 12.0,
                'total_duration': 6000,
            },
        }

    def test_it_get_stats_for_sport_1(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport?sport_id=1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '1': {
                'nb_activities': 7,
                'total_distance': 54.0,
                'total_duration': 16104,
            }
        }

    def test_it_returns_errors_if_user_does_not_exist(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/stats/1000/by_sport?sport_id=1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'User does not exist.' in data['message']

    def test_it_returns_error_if_sport_does_not_exist(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport?sport_id=999',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'Sport does not exist.' in data['message']

    def test_it_returns_error_if_sport_id_is_invalid(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        seven_activities_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport?sport_id="999',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'Error. Please try again or contact the administrator.'
            in data['message']
        )


class TestGetAllStats:
    def test_it_returns_all_stats_when_users_have_no_activities(
        self, app, user_1_admin, user_2
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['activities'] == 0
        assert data['data']['sports'] == 0
        assert data['data']['users'] == 2
        assert 'uploads_dir_size' in data['data']

    def test_it_gets_app_all_stats_with_activities(
        self,
        app,
        user_1_admin,
        user_2,
        user_3,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
        activity_cycling_user_2,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
            content_type='application/json',
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['activities'] == 3
        assert data['data']['sports'] == 2
        assert data['data']['users'] == 3
        assert 'uploads_dir_size' in data['data']

    def test_it_returns_error_if_user_has_no_admin_rights(
        self,
        app,
        user_1,
        user_2,
        user_3,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
        activity_cycling_user_2,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'success' not in data['status']
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']
