from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .utils import TEST_URL, register_valid_user


class TestWorkout:
    def test_user_can_add_workout_without_gpx(self, selenium):
        register_valid_user(selenium)
        app_menu = selenium.find_element(By.CLASS_NAME, 'nav-items-app-menu')
        add_workout_link = app_menu.find_elements(By.CLASS_NAME, 'nav-item')[3]

        add_workout_link.click()
        selenium.implicitly_wait(1)
        radio_button = selenium.find_element(By.ID, 'withoutGpx')
        radio_button.click()

        select = Select(selenium.find_element(By.ID, 'sport'))
        select.select_by_index(1)
        selenium.find_element(By.NAME, 'title').send_keys('Workout title')
        selenium.find_element(By.NAME, 'workout-date').send_keys('2018-12-20')
        selenium.find_element(By.NAME, 'workout-time').send_keys('14:05')
        selenium.find_element(By.NAME, 'workout-duration-hour').send_keys('01')
        selenium.find_element(By.NAME, 'workout-duration-minutes').send_keys(
            '00'
        )
        selenium.find_element(By.NAME, 'workout-duration-seconds').send_keys(
            '00'
        )
        selenium.find_element(By.NAME, 'workout-distance').send_keys('10')

        confirm_button = selenium.find_elements(By.CLASS_NAME, 'confirm')[-1]
        confirm_button.click()

        WebDriverWait(selenium, 10).until(
            EC.url_changes(f"{TEST_URL}/workouts/add")
        )

        workout_details = selenium.find_element(By.ID, 'workout-info').text
        assert 'Duration: 1:00:00' in workout_details
        assert 'Distance: 10 km' in workout_details
        assert 'Average Speed: 10 km/h' in workout_details
        assert 'Max. Speed: 10 km/h' in workout_details
