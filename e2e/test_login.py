from .utils import (
    TEST_URL,
    assert_navbar,
    login_valid_user,
    register_valid_user_and_logout,
)

URL = f'{TEST_URL}/login'


class TestLogin:
    def test_navbar_contains_login(self, selenium):
        selenium.get(URL)

        nav = selenium.find_element_by_id('nav').text
        assert 'Login' in nav

    def test_it_displays_login_form(self, selenium):
        selenium.get(URL)

        inputs = selenium.find_elements_by_tag_name('input')
        assert len(inputs) == 2
        assert inputs[0].get_attribute('id') == 'email'
        assert inputs[0].get_attribute('type') == 'email'
        assert inputs[1].get_attribute('id') == 'password'
        assert inputs[1].get_attribute('type') == 'password'

        button = selenium.find_element_by_tag_name('button')
        assert button.get_attribute('type') == 'submit'
        assert 'Log in' in button.text

        links = selenium.find_elements_by_class_name('links')
        assert links[0].tag_name == 'a'
        assert 'Register' in links[0].text
        assert links[1].tag_name == 'a'
        assert 'Forgot password?' in links[1].text

    def test_user_can_log_in(self, selenium):
        user = register_valid_user_and_logout(selenium)

        login_valid_user(selenium, user)

        assert_navbar(selenium, user)
