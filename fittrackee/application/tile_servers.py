import os
import random
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TileProviderBase:
    attribution: str
    name: str
    url_template: str
    subdomains: str = ""
    apikey: str = ""
    style: str = ""

    @property
    def url(self) -> str:
        url = self.url_template
        if self.style:
            url = url.replace("{style}", self.style)
        if self.subdomains:
            subdomains = self.subdomains.split(",")
            url = url.replace("{s}", random.choice(subdomains))  # noqa:S311
        if self.apikey:
            url = url.replace("{apikey}", self.apikey)
        return url


# commons
SUBDOMAINS = "a,b,c"


# Openstreetmap
@dataclass(kw_only=True)
class OSMTileProvider(TileProviderBase):
    attribution: str = (
        '&copy; <a href="http://www.openstreetmap.org/copyright" '
        'target="_blank" rel="noopener noreferrer">OpenStreetMap</a>'
        " contributors"
    )


OSM_TILE_PROVIDERS = {
    "osm": OSMTileProvider(
        name="OSM",
        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    ),
    "osm_de": OSMTileProvider(
        name="OSM (de)",
        url_template="https://tile.openstreetmap.de/{z}/{x}/{y}.png",
    ),
    "osm_fr": OSMTileProvider(
        name="OSM (fr)",
        url_template="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
    ),
    "cyclosm": OSMTileProvider(
        attribution=(
            '<a href="https://github.com/cyclosm/cyclosm-cartocss-style/'
            'releases" title="CyclOSM - Open Bicycle render">CyclOSM</a> | '
            'Map data: &copy; <a href="https://www.openstreetmap.org/copyright"'
            ">OpenStreetMap</a> contributors"
        ),
        name="CyclOSM",
        subdomains=SUBDOMAINS,
        url_template=(
            "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png"
        ),
    ),
}


# Stadia Maps
@dataclass(kw_only=True)
class StadiaTileProvider(TileProviderBase):
    apikey: str = os.getenv("STADIAMAPS_API_KEY", "")
    attribution: str = (
        '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia '
        'Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">'
        'OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/'
        'copyright" target="_blank">OpenStreetMap</a>'
    )
    url_template: str = (
        "https://tiles.stadiamaps.com/tiles/{style}/{z}/{x}/{y}.png?"
        "apikey={apikey}"
    )


STADIAMAPS_TILE_PROVIDERS = {
    "stadiamaps_alidade_smooth": StadiaTileProvider(
        name="Stadia Alidade Smooth", style="alidade_smooth"
    ),
    "stadiamaps_outdoors": StadiaTileProvider(
        name="Stadia Outdoors", style="outdoors"
    ),
}


# Thunderforest
@dataclass(kw_only=True)
class ThunderForestTileProvider(TileProviderBase):
    apikey: str = os.getenv("THUNDERFOREST_API_KEY", "")
    attribution: str = (
        '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>,'
        ' &copy; <a href="http://www.openstreetmap.org/copyright">'
        "OpenStreetMap</a> contributors"
    )
    url_template: str = (
        "https://api.thunderforest.com/{style}/{z}/{x}/{y}.png?apikey={apikey}"
    )


THUNDERFOREST_TILE_PROVIDERS = {
    "thunderforest_outdoor": ThunderForestTileProvider(
        name="Thunderforest Outdoors", style="outdoors"
    ),
    "thunderforest_landscape": ThunderForestTileProvider(
        name="Thunderforest Landscape", style="landscape"
    ),
}
TILE_PROVIDERS: Dict[str, TileProviderBase] = {
    **OSM_TILE_PROVIDERS,
    **STADIAMAPS_TILE_PROVIDERS,
    **THUNDERFOREST_TILE_PROVIDERS,
}
DEFAULT_TILE_PROVIDER: TileProviderBase = TILE_PROVIDERS["osm"]


# Custom
def get_tile_provider_from_env_var() -> Dict:
    tile_server_url = os.environ.get("TILE_SERVER_URL", "")
    if not tile_server_url:
        return {}

    return {
        "attribution": os.environ.get("MAP_ATTRIBUTION", ""),
        "subdomains": os.environ.get("STATICMAP_SUBDOMAINS", ""),
        "name": "Custom",
        "url_template": tile_server_url,
    }


custom_provider = get_tile_provider_from_env_var()
if custom_provider:
    TILE_PROVIDERS["custom"] = TileProviderBase(**custom_provider)


def get_custom_tile_provider() -> List[str]:
    tile_server_url = os.environ.get("TILE_SERVER_URL", "")
    if tile_server_url:
        return ["custom"]
    return []
