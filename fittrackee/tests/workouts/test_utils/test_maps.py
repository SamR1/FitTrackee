from unittest.mock import patch

import pytest

from fittrackee.workouts.utils.maps import get_static_map_tile_server_url


class TestGetStaticMapTileServerUrl:
    @pytest.mark.parametrize(
        'input_tile_server_url,'
        'input_tile_server_subdomains,'
        'expected_tile_server_url',
        [
            (
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                '',
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            ),
            (
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                'a',
                'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
            ),
            (
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                '',
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            ),
            (
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                'a',
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            ),
        ],
    )
    def test_it_returns_tile_server_url(
        self,
        input_tile_server_url: str,
        input_tile_server_subdomains: str,
        expected_tile_server_url: str,
    ) -> None:
        tile_config = {
            'URL': input_tile_server_url,
            'STATICMAP_SUBDOMAINS': input_tile_server_subdomains,
        }

        assert (
            get_static_map_tile_server_url(tile_config)
            == expected_tile_server_url
        )

    def test_it_returns_tile_server_url_with_random_subdomain(self) -> None:
        """in case multiple subdomains are provided"""
        tile_config = {
            'URL': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            'STATICMAP_SUBDOMAINS': 'a,b,c',
        }

        with patch('random.choice', return_value='b'):
            assert (
                get_static_map_tile_server_url(tile_config)
                == 'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png'
            )
