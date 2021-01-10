from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .utils import TEST_URL, register_valid_user


class TestWorkout:
    def test_user_can_add_workout_without_gpx(self, selenium):
        register_valid_user(selenium)
        nav_items = selenium.find_elements_by_class_name('nav-item')

        nav_items[3].click()
        selenium.implicitly_wait(1)
        radio_buttons = selenium.find_elements_by_class_name(
            'add-workout-radio'
        )
        radio_buttons[1].click()

        selenium.find_element_by_name('title').send_keys('Workout title')
        select = Select(selenium.find_element_by_name('sport_id'))
        select.select_by_index(1)
        selenium.find_element_by_name('workout_date').send_keys('2018-12-20')
        selenium.find_element_by_name('workout_time').send_keys('14:05')
        selenium.find_element_by_name('duration').send_keys('01:00:00')
        selenium.find_element_by_name('distance').send_keys('10')
        selenium.find_element_by_class_name('btn-primary').click()

        WebDriverWait(selenium, 10).until(
            EC.url_changes(f"{TEST_URL}/workouts/add")
        )

        workout_details = selenium.find_element_by_class_name(
            'workout-details'
        ).text
        assert 'Duration: 1:00:00' in workout_details
        assert 'Distance: 10 km' in workout_details
        assert 'Average speed: 10 km/h' in workout_details
        assert 'Max. speed: 10 km/h' in workout_details
