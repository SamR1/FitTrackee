from mpwo_api.tests.utils import add_user


def test_add_user(app):
    user = add_user('test', 'test@test.com', '12345678')
    assert '<User \'test\'>' == str(user)

