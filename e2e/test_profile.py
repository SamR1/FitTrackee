from .utils import register_valid_user


class TestProfile:
    def test_it_displays_user_profile(self, selenium):
        user = register_valid_user(selenium)

        app_menu = selenium.find_element_by_class_name('nav-items-user-menu')
        profile_link = app_menu.find_elements_by_class_name('nav-item')[1]
        profile_link.click()
        selenium.implicitly_wait(1)

        user_header = selenium.find_element_by_class_name('user-header')
        assert user['username'] in user_header.text
        assert '0\nworkouts' in user_header.text
        assert '0\nkm' in user_header.text
        assert '0\nsports' in user_header.text

        user_infos = selenium.find_element_by_id('user-infos')
        assert 'Registration date' in user_infos.text
        assert 'First name' in user_infos.text
        assert 'Last name' in user_infos.text
        assert 'Birth date' in user_infos.text
        assert 'Location' in user_infos.text
        assert 'Bio' in user_infos.text
