from selenium.webdriver.common.by import By

from .utils import register_valid_user


class TestLogout:
    def test_user_can_log_out(self, selenium):
        user = register_valid_user(selenium)
        logout_button = selenium.find_elements(By.CLASS_NAME, 'logout-button')[
            0
        ]

        logout_button.click()
        modal = selenium.find_element(By.ID, 'modal')
        confirm_button = modal.find_elements(By.CLASS_NAME, 'confirm')[0]
        confirm_button.click()
        selenium.implicitly_wait(1)

        nav = selenium.find_element(By.ID, 'nav').text
        assert 'Register' in nav
        assert 'Login' in nav
        assert user['username'] not in nav
        buttons = selenium.find_elements(By.CLASS_NAME, 'logout-button')
        assert buttons == []
