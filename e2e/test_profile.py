from selenium.webdriver.common.by import By

from .utils import register_valid_user


class TestProfile:
    def test_it_displays_user_profile(self, selenium):
        user = register_valid_user(selenium)

        app_menu = selenium.find_element(By.CLASS_NAME, 'nav-items-user-menu')
        profile_link = app_menu.find_elements(By.CLASS_NAME, 'nav-item')[0]
        profile_link.click()
        selenium.implicitly_wait(1)

        user_header = selenium.find_element(By.CLASS_NAME, 'user-header')
        assert user['username'] in user_header.text
        assert '0\nworkouts' in user_header.text
        assert '0\nfollowing' in user_header.text
        assert '0\nfollowers' in user_header.text

        user_infos = selenium.find_element(By.ID, 'user-infos')
        assert 'Registration date' in user_infos.text
        assert 'First name' not in user_infos.text
        assert 'Last name' not in user_infos.text
        assert 'Birth date' not in user_infos.text
        assert 'Location' not in user_infos.text
        assert 'Bio' not in user_infos.text
