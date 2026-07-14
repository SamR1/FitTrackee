from requests.structures import CaseInsensitiveDict

from fittrackee.workouts.workouts import get_tile_response_headers


class TestGetTileResponseHeaders:
    @staticmethod
    def test_it_returns_cache_headers() -> None:
        headers = CaseInsensitiveDict(
            {
                "content-type": "image/png",
                "Cache-Control": (
                    "max-age=86400, stale-while-revalidate=604800"
                ),
                "ETag": '"tile-etag"',
                "Expires": "Wed, 24 Jun 2026 16:46:03 GMT",
                "Last-Modified": "Tue, 23 Jun 2026 16:46:03 GMT",
                "Age": "3600",
                "Server": "upstream",
            }
        )

        response_headers = get_tile_response_headers(headers)

        assert (
            response_headers["Cache-Control"]
            == "max-age=86400, stale-while-revalidate=604800"
        )
        assert response_headers["ETag"] == '"tile-etag"'
        assert response_headers["Expires"] == "Wed, 24 Jun 2026 16:46:03 GMT"
        assert (
            response_headers["Last-Modified"]
            == "Tue, 23 Jun 2026 16:46:03 GMT"
        )
        assert response_headers["Age"] == "3600"
        assert "content-type" not in response_headers
        assert "Server" not in response_headers
