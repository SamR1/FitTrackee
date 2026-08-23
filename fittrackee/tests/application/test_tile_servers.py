from typing import TYPE_CHECKING

from fittrackee.application.tile_servers import TileProviderBase

if TYPE_CHECKING:
    import pytest


class TestTileProviderBase:
    def test_it_instantiates_tile_provider_with_minimal_value(
        self,
    ) -> None:
        tile_config = {
            "attribution": (
                '&copy; <a href="http://www.openstreetmap.org/copyright" '
                'target="_blank" rel="noopener noreferrer">OpenStreetMap</a>'
                " contributors"
            ),
            "name": "OSM",
            "url_template": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        }

        tile_provider = TileProviderBase(**tile_config)

        assert tile_provider.apikey == ""
        assert tile_provider.api_key_is_missing is False
        assert tile_provider.apikey_value == ""
        assert tile_provider.attribution == tile_config["attribution"]
        assert tile_provider.link == ""
        assert tile_provider.name == tile_config["name"]
        assert tile_provider.subdomains == ""
        assert tile_provider.style == ""
        assert tile_provider.url == tile_config["url_template"]
        assert tile_provider.url_template == tile_config["url_template"]
        assert tile_provider.url_with_style == tile_config["url_template"]
        assert tile_provider.url_with_subdomain == tile_config["url_template"]

    def test_it_instantiates_tile_provider_with_all_values(
        self, monkeypatch: "pytest.MonkeyPatch"
    ) -> None:
        api_key_value = "some-value"
        monkeypatch.setenv("SOME_KEY", api_key_value)
        tile_config = {
            "attribution": (
                '&copy; Custom <a href="http://www.openstreetmap.org/copyright"'
                ' target="_blank" rel="noopener noreferrer">OpenStreetMap</a>'
                " contributors"
            ),
            "name": "OSM Custom",
            "url_template": (
                "https://{s}.tile.openstreetmap.org/{style}/{z}/{x}/{y}.png?"
                "apikey={apikey}"
            ),
            "subdomains": "a",
            "apikey": "SOME_KEY",
            "style": "outdoors",
            "link": "https://example.com",
        }

        tile_provider = TileProviderBase(**tile_config)

        assert tile_provider.apikey == tile_config["apikey"]
        assert tile_provider.api_key_is_missing is False
        assert tile_provider.apikey_value == api_key_value
        assert tile_provider.attribution == tile_config["attribution"]
        assert tile_provider.link == tile_config["link"]
        assert tile_provider.name == tile_config["name"]
        assert tile_provider.subdomains == tile_config["subdomains"]
        assert tile_provider.style == tile_config["style"]
        assert tile_provider.url == (
            "https://{s}.tile.openstreetmap.org/"
            f"{tile_config['style']}"
            "/{z}/{x}/{y}.png?apikey="
            f"{api_key_value}"
        )
        assert tile_provider.url_template == tile_config["url_template"]
        assert tile_provider.url_with_style == (
            "https://{s}.tile.openstreetmap.org/"
            f"{tile_config['style']}"
            "/{z}/{x}/{y}.png?apikey={apikey}"
        )
        assert tile_provider.url_with_subdomain == (
            f"https://{tile_config['subdomains']}.tile.openstreetmap.org/"
            f"{tile_config['style']}"
            "/{z}/{x}/{y}.png?apikey="
            f"{api_key_value}"
        )

    def test_api_missing_is_true_when_api_key_is_not_set(
        self,
    ) -> None:
        tile_config = {
            "attribution": (
                '&copy; Custom <a href="http://www.openstreetmap.org/copyright"'
                ' target="_blank" rel="noopener noreferrer">OpenStreetMap</a>'
                " contributors"
            ),
            "name": "OSM Custom",
            "url_template": (
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png?"
                "apikey={apikey}"
            ),
            "subdomains": "",
            "apikey": "SOME_KEY",
            "style": "",
        }

        tile_provider = TileProviderBase(**tile_config)

        assert tile_provider.apikey == "SOME_KEY"
        assert tile_provider.api_key_is_missing is True
        assert tile_provider.apikey_value == ""
