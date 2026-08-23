import os
import random
from dataclasses import dataclass
from typing import Dict


# commons
@dataclass
class TileProviderBase:
    attribution: str
    name: str
    url_template: str
    subdomains: str = ""
    apikey: str = ""
    apikey_value: str = ""
    style: str = ""
    link: str = ""

    def __post_init__(self) -> None:
        if self.apikey:
            self.apikey_value = os.getenv(self.apikey, "")

    @property
    def url_with_style(self) -> str:
        url = self.url_template
        if self.style:
            url = url.replace("{style}", self.style)
        return url

    @property
    def url(self) -> str:
        url = self.url_with_style
        if self.apikey_value:
            url = url.replace("{apikey}", self.apikey_value)
        return url

    @property
    def url_with_subdomain(self) -> str:
        url = self.url
        if self.subdomains:
            subdomains = self.subdomains.split(",")
            url = url.replace("{s}", random.choice(subdomains))  # noqa:S311
        return url

    @property
    def api_key_is_missing(self) -> bool:
        return "{apikey}" in self.url_template and not self.apikey_value


SUBDOMAINS = "a,b,c"


# Openstreetmap
@dataclass(kw_only=True)
class OSMTileProvider(TileProviderBase):
    attribution: str = (
        '&copy; <a href="http://www.openstreetmap.org/copyright" '
        'target="_blank" rel="noopener noreferrer">OpenStreetMap</a>'
        " contributors"
    )


# Stadia Maps
@dataclass(kw_only=True)
class StadiaTileProvider(TileProviderBase):
    apikey: str = "STADIAMAPS_API_KEY"
    attribution: str = (
        '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia '
        'Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">'
        'OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/'
        'copyright" target="_blank">OpenStreetMap</a>'
    )
    url_template: str = (
        "https://tiles.stadiamaps.com/tiles/{style}/{z}/{x}/{y}.png?"
        "api_key={apikey}"
    )


# Thunderforest
@dataclass(kw_only=True)
class ThunderForestTileProvider(TileProviderBase):
    apikey: str = "THUNDERFOREST_API_KEY"
    attribution: str = (
        '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>,'
        ' &copy; <a href="http://www.openstreetmap.org/copyright">'
        "OpenStreetMap</a> contributors"
    )
    url_template: str = (
        "https://api.thunderforest.com/{style}/{z}/{x}/{y}.png?apikey={apikey}"
    )


# Custom
def _get_custom_tile_provider_url() -> str:
    return os.environ.get(
        "CUSTOM_TILE_PROVIDER_URL", os.environ.get("TILE_SERVER_URL", "")
    )


def get_custom_tile_provider() -> str:
    tile_server_url = _get_custom_tile_provider_url()
    return "custom" if tile_server_url else "osm"


def get_tile_provider_from_env_var() -> Dict:
    """
    For tile provider set before v1.4.0, the environment variables are:
    - TILE_SERVER_URL
    - MAP_ATTRIBUTION
    - STATICMAP_SUBDOMAINS
    These variables are deprecated. Use variables with prefix
    'CUSTOM_TILE_PROVIDER_' instead.
    """
    tile_server_url = _get_custom_tile_provider_url()
    if not tile_server_url:
        return {}

    return {
        "attribution": os.environ.get(
            "CUSTOM_TILE_PROVIDER_ATTRIBUTION",
            os.environ.get("MAP_ATTRIBUTION", ""),
        ),
        "subdomains": os.environ.get(
            "CUSTOM_TILE_PROVIDER_SUBDOMAINS",
            os.environ.get("STATICMAP_SUBDOMAINS", ""),
        ),
        "name": "Custom",
        "url_template": tile_server_url,
    }
