from .utils import TEST_URL, register_valid_user

URL = f'{TEST_URL}/profile'


class TestProfile:
    def test_it_displays_user_profile(self, selenium):
        user = register_valid_user(selenium)

        selenium.get(URL)

        assert 'Profile' in selenium.find_element_by_tag_name('h1').text
        assert (
            user['username']
            in selenium.find_element_by_class_name('userName').text
        )
        assert (
            user['username']
            in selenium.find_element_by_class_name('userName').text
        )
