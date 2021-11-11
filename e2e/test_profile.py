from .utils import TEST_URL, register_valid_user

URL = f'{TEST_URL}/profile'


class TestProfile:
    def test_it_displays_user_profile(self, selenium):
        user = register_valid_user(selenium)

        selenium.get(URL)
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
