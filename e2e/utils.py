import os
import random
import string

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TEST_APP_URL = os.getenv('TEST_APP_URL')
TEST_CLIENT_URL = os.getenv('TEST_CLIENT_URL')
E2E_ARGS = os.getenv('E2E_ARGS')
TEST_URL = TEST_CLIENT_URL if E2E_ARGS == 'client' else TEST_APP_URL


def random_string(length=8):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


def register(selenium, user):
    selenium.get(f'{TEST_URL}/register')
    selenium.implicitly_wait(1)
    username = selenium.find_element_by_id('username')
    username.send_keys(user.get('username'))
    email = selenium.find_element_by_id('email')
    email.send_keys(user.get('email'))
    password = selenium.find_element_by_id('password')
    password.send_keys(user.get('password'))
    submit_button = selenium.find_element_by_tag_name('button')
    submit_button.click()


def login(selenium, user):
    selenium.get(f'{TEST_URL}/login')
    selenium.implicitly_wait(1)
    email = selenium.find_element_by_id('email')
    email.send_keys(user.get('email'))
    password = selenium.find_element_by_id('password')
    password.send_keys(user.get('password'))
    submit_button = selenium.find_element_by_tag_name('button')
    submit_button.click()


def register_valid_user(selenium):
    user_name = random_string()
    user = {
        'username': user_name,
        'email': f'{user_name}@example.com',
        'password': 'p@ssw0rd',
    }
    register(selenium, user)
    WebDriverWait(selenium, 15).until(EC.url_changes(f"{TEST_URL}/register"))
    return user


def register_valid_user_and_logout(selenium):
    user_name = random_string()
    user = {
        'username': user_name,
        'email': f'{user_name}@example.com',
        'password': 'p@ssw0rd',
    }
    register(selenium, user)
    WebDriverWait(selenium, 15).until(EC.url_changes(f"{TEST_URL}/register"))

    user_menu = selenium.find_element_by_class_name('nav-items-user-menu')
    logout_link = user_menu.find_elements_by_class_name('nav-item')[2]
    logout_link.click()
    selenium.implicitly_wait(1)
    return user


def login_valid_user(selenium, user):
    login(selenium, user)
    WebDriverWait(selenium, 10).until(EC.url_changes(f"{TEST_URL}/login"))
    return user


def assert_navbar(selenium, user):
    nav = selenium.find_element_by_id('nav').text
    assert 'Register' not in nav
    assert 'Login' not in nav
    assert 'Dashboard' in nav
    assert 'Workouts' in nav
    assert 'Statistics' in nav
    assert 'Add a workout' in nav
    assert user['username'] in nav
    assert 'Logout' in nav
