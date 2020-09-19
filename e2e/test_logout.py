from .utils import register_valid_user


class TestLogout:
    def test_user_can_log_out(self, selenium):
        user = register_valid_user(selenium)
        nav_items = selenium.find_elements_by_class_name('nav-item')

        nav_items[5].click()
        selenium.implicitly_wait(1)

        nav = selenium.find_element_by_tag_name('nav').text
        assert 'Register' in nav
        assert 'Login' in nav
        assert user['username'] not in nav
        assert 'Logout' not in nav

        message = selenium.find_element_by_class_name('card-body').text
        assert 'You are now logged out. Click here to log back in.' in message
