from mpwo_api.tests.utils import add_sport, add_user


def test_add_sport(app):
    add_user('test', 'test@test.com', '12345678')
    sport = add_sport('cycling')

    assert 1 == sport.id
    assert 'cycling' == sport.label
    assert '<Sport \'cycling\'>' == str(sport)
