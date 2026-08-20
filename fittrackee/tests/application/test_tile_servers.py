from fittrackee.application.tile_servers import TileProviderBase


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

        assert tile_provider.attribution == tile_config["attribution"]
        assert tile_provider.name == tile_config["name"]
        assert tile_provider.url_template == tile_config["url_template"]
        assert tile_provider.subdomains == ""
        assert tile_provider.apikey == ""
        assert tile_provider.style == ""
        assert tile_provider.url == tile_config["url_template"]

    def test_it_instantiates_tile_provider_with_all_value(
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
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?"
                "apikey={apikey}"
            ),
            "subdomains": "a",
            "apikey": "SOME_KEY",
            "style": "outdoors",
        }

        tile_provider = TileProviderBase(**tile_config)

        assert tile_provider.attribution == tile_config["attribution"]
        assert tile_provider.name == tile_config["name"]
        assert tile_provider.url_template == tile_config["url_template"]
        assert tile_provider.subdomains == tile_config["subdomains"]
        assert tile_provider.apikey == tile_config["apikey"]
        assert tile_provider.style == tile_config["style"]
        assert tile_provider.url == (
            f"https://{tile_config['subdomains']}.tile.openstreetmap.org/"
            "{z}/{x}/{y}.png?apikey="
            f"{tile_config['apikey']}"
        )
