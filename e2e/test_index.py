from .utils import TEST_URL


class TestIndex:
    def test_title_contains_fittrackee(self, selenium):
        selenium.get(TEST_URL)
        assert 'FitTrackee' in selenium.title

    def test_navbar_contains_all_links(self, selenium):
        selenium.get(TEST_URL)

        nav = selenium.find_element_by_tag_name('nav').text
        assert "FitTrackee" in nav
        assert "Dashboard" in nav
        assert "Login" in nav
        assert "Register" in nav
        assert "en" in nav
