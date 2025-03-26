import os
import random
import re
import string
import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.util import parse_url

TEST_APP_URL = os.getenv("TEST_APP_URL")
TEST_CLIENT_URL = os.getenv("TEST_CLIENT_URL")
E2E_ARGS = os.getenv("E2E_ARGS")
TEST_URL = TEST_CLIENT_URL if E2E_ARGS == "client" else TEST_APP_URL
EMAIL_URL = os.getenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
parsed_email_url = parse_url(EMAIL_URL)
EMAIL_API_URL = f"http://{parsed_email_url.host}:8025"


def random_string(length=8):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def register(selenium, user):
    selenium.get(f"{TEST_URL}/register")
    selenium.implicitly_wait(1)
    user_form = selenium.find_element(By.ID, "user-form")
    username = user_form.find_element(By.ID, "username")
    username.send_keys(user.get("username"))
    email = user_form.find_element(By.ID, "email")
    email.send_keys(user.get("email"))
    password = user_form.find_element(By.ID, "password")
    password.send_keys(user.get("password"))
    accepted_policy = user_form.find_element(By.ID, "accepted_policy")
    accepted_policy.click()
    submit_button = user_form.find_elements(By.TAG_NAME, "button")[-1]
    submit_button.click()


def login(selenium, user):
    selenium.get(f"{TEST_URL}/login")
    selenium.implicitly_wait(1)
    user_form = selenium.find_element(By.ID, "user-form")
    email = user_form.find_element(By.ID, "email")
    email.send_keys(user.get("email"))
    password = user_form.find_element(By.ID, "password")
    password.send_keys(user.get("password"))
    submit_button = user_form.find_elements(By.TAG_NAME, "button")[-1]
    submit_button.click()


def register_valid_user(selenium):
    user_name = random_string()
    user = {
        "username": user_name,
        "email": f"{user_name}@example.com",
        "password": "p@ssw0rd",
    }
    register(selenium, user)
    WebDriverWait(selenium, 30).until(EC.url_changes(f"{TEST_URL}/register"))
    confirm_account(selenium, user)
    return user


def register_valid_user_and_logout(selenium):
    user = register_valid_user(selenium)
    user_menu = selenium.find_element(By.CLASS_NAME, "nav-items-user-menu")
    logout_button = user_menu.find_elements(By.CLASS_NAME, "logout-button")[0]
    logout_button.click()
    modal = selenium.find_element(By.ID, "modal")
    confirm_button = modal.find_elements(By.CLASS_NAME, "confirm")[0]
    confirm_button.click()
    selenium.implicitly_wait(1)
    return user


def confirm_account(selenium, user):
    time.sleep(1)
    response = requests.get(
        f"{EMAIL_API_URL}/api/v2/search?kind=to&query={user['email']}"
    )
    response.raise_for_status()
    results = response.json()
    message = results["items"][0]["Content"]["Body"]
    link = re.search(r"Verify your email: (.+?)\r\n", message).groups()[0]
    link = link.replace("http://0.0.0.0:5000", TEST_URL)
    selenium.get(link)
    WebDriverWait(selenium, 15).until(EC.url_changes(link))


def login_valid_user(selenium, user):
    login(selenium, user)
    WebDriverWait(selenium, 10).until(EC.url_changes(f"{TEST_URL}/login"))
    return user
