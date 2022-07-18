from selenium.webdriver.common.by import By

from .utils import (
    TEST_URL,
    random_string,
    register,
    register_valid_user_and_logout,
)

URL = f'{TEST_URL}/register'


class TestRegistration:
    def test_it_displays_registration_form(self, selenium):
        selenium.get(URL)
        selenium.implicitly_wait(1)

        inputs = selenium.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 4
        assert inputs[0].get_attribute('id') == 'username'
        assert inputs[0].get_attribute('type') == 'text'
        assert inputs[1].get_attribute('id') == 'email'
        assert inputs[1].get_attribute('type') == 'email'
        assert inputs[2].get_attribute('id') == 'password'
        assert inputs[2].get_attribute('type') == 'password'

        form_infos = selenium.find_elements(By.CLASS_NAME, 'form-info')
        assert len(form_infos) == 3
        assert form_infos[0].text == (
            '3 to 30 characters required, only alphanumeric characters and '
            'the underscore character "_" allowed.'
        )
        assert form_infos[1].text == 'Enter a valid email address.'
        assert form_infos[2].text == 'At least 8 characters required.'

        button = selenium.find_element(By.TAG_NAME, 'button')
        assert button.get_attribute('type') == 'submit'
        assert 'Register' in button.text

        links = selenium.find_elements(By.CLASS_NAME, 'links')
        assert links[0].tag_name == 'a'
        assert 'Login' in links[0].text
        assert links[1].tag_name == 'a'
        assert "Didn't received instructions?" in links[1].text

    def test_user_can_register(self, selenium):
        user = {
            'username': random_string(),
            'email': f'{random_string()}@example.com',
            'password': 'p@ssw0rd',
        }

        register(selenium, user)

        message = selenium.find_element(By.CLASS_NAME, 'success-message').text
        assert (
            'A link to activate your account has been '
            'emailed to the address provided.'
        ) in message

    def test_user_can_not_register_with_invalid_email(self, selenium):
        user_name = random_string()
        user_infos = {
            'username': user_name,
            'email': user_name,
            'password': 'p@ssw0rd',
        }

        register(selenium, user_infos)

        assert selenium.current_url == URL
        nav = selenium.find_element(By.ID, 'nav').text
        assert 'Register' in nav
        assert 'Login' in nav

    def test_user_can_not_register_if_username_is_already_taken(
        self, selenium
    ):
        user = register_valid_user_and_logout(selenium)
        user['email'] = f'{random_string()}@example.com'

        register(selenium, user)

        assert selenium.current_url == URL
        errors = selenium.find_element(By.CLASS_NAME, 'error-message').text
        assert 'Sorry, that username is already taken.' in errors

    def test_user_does_not_return_error_if_email_is_already_taken(
        self, selenium
    ):
        user = register_valid_user_and_logout(selenium)
        user['username'] = random_string()

        register(selenium, user)

        assert selenium.current_url == f'{TEST_URL}/login'
        message = selenium.find_element(By.CLASS_NAME, 'success-message').text
        assert (
            'A link to activate your account has been '
            'emailed to the address provided.'
        ) in message
