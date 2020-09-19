from .utils import TEST_URL, assert_navbar, login_valid_user

URL = f'{TEST_URL}/login'


class TestLogin:
    def test_navbar_contains_login(self, selenium):
        selenium.get(URL)

        nav = selenium.find_element_by_tag_name('nav').text
        assert 'Login' in nav

    def test_h1_contains_login(self, selenium):
        selenium.get(URL)

        title = selenium.find_element_by_tag_name('h1').text
        assert 'Login' in title

    def test_it_displays_login_form(self, selenium):
        selenium.get(URL)

        inputs = selenium.find_elements_by_tag_name('input')
        assert len(inputs) == 3
        assert inputs[0].get_attribute('name') == 'email'
        assert inputs[0].get_attribute('type') == 'email'
        assert inputs[1].get_attribute('name') == 'password'
        assert inputs[1].get_attribute('type') == 'password'
        assert inputs[2].get_attribute('name') == ''
        assert inputs[2].get_attribute('type') == 'submit'

    def test_user_can_log_in(self, selenium):
        user = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'mpwoadmin',
        }

        login_valid_user(selenium, user)

        assert_navbar(selenium, user)
