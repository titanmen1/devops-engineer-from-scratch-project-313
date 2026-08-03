from collections.abc import Callable

from httpx import AsyncClient
from sqlmodel import Session

from app.models import URL

UNKNOWN_LINK_ID = 999999


class TestPing:
    """Проверка доступности приложения"""

    async def test_answers_pong(self, client: AsyncClient) -> None:
        response = await client.get("/ping")

        assert response.status_code == 200
        assert response.json() == "pong"


class TestLinks:
    """Ресурс /api/links"""

    class TestList:
        async def test_returns_empty_list_without_links(
            self, client: AsyncClient
        ) -> None:
            response = await client.get("/api/links")

            assert response.status_code == 200
            assert response.json() == []
            assert response.headers["Content-Range"] == "links 0--1/0"

        async def test_returns_saved_links(
            self, client: AsyncClient, links: list[URL]
        ) -> None:
            response = await client.get("/api/links")

            assert response.status_code == 200
            data = response.json()
            assert {item["short_name"] for item in data} == {
                link.short_name for link in links
            }
            assert response.headers["Content-Range"] == "links 0-2/3"

        async def test_returns_page_from_range(
            self, client: AsyncClient, many_links: list[URL]
        ) -> None:
            response = await client.get("/api/links?range=[0,10]")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 10
            assert {item["id"] for item in data} <= {link.id for link in many_links}
            assert response.headers["Content-Range"] == "links 0-9/15"

        async def test_returns_empty_page_beyond_data(
            self, client: AsyncClient, many_links: list[URL]
        ) -> None:
            response = await client.get("/api/links?range=[20,30]")

            assert response.status_code == 200
            assert response.json() == []
            assert response.headers["Content-Range"] == "links 20-20/15"

        async def test_limits_page_size_without_range(
            self, client: AsyncClient, many_links: list[URL]
        ) -> None:
            response = await client.get("/api/links")

            assert response.status_code == 200
            assert len(response.json()) == 10
            assert response.headers["Content-Range"] == "links 0-9/15"

    class TestDetail:
        async def test_returns_link_by_id(self, client: AsyncClient, link: URL) -> None:
            response = await client.get(f"/api/links/{link.id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == link.id
            assert data["original_url"] == link.original_url
            assert data["short_name"] == link.short_name
            assert data["short_url"].endswith(f"/r/{link.short_name}")

        async def test_returns_404_for_unknown_link(self, client: AsyncClient) -> None:
            response = await client.get(f"/api/links/{UNKNOWN_LINK_ID}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    class TestCreate:
        async def test_saves_link(
            self, client: AsyncClient, db_session: Session
        ) -> None:
            payload = {"original_url": "https://example.com", "short_name": "example"}

            response = await client.post("/api/links", json=payload)

            assert response.status_code == 201
            data = response.json()
            assert data["original_url"] == payload["original_url"]
            assert data["short_name"] == payload["short_name"]

            created = db_session.get(URL, data["id"])
            assert created is not None
            assert created.original_url == payload["original_url"]
            assert created.short_name == payload["short_name"]

        async def test_requires_short_name(self, client: AsyncClient) -> None:
            payload = {"original_url": "https://example.com", "short_name": ""}

            response = await client.post("/api/links", json=payload)

            assert response.status_code == 400
            assert "short_name" in response.json()["detail"]

        async def test_rejects_duplicate_short_name(
            self, client: AsyncClient, link: URL
        ) -> None:
            payload = {"original_url": "https://other.com", "short_name": "example"}

            response = await client.post("/api/links", json=payload)

            assert response.status_code == 400
            assert "already exists" in response.json()["detail"]

    class TestUpdate:
        async def test_saves_changes(
            self, client: AsyncClient, db_session: Session, link: URL
        ) -> None:
            payload = {"original_url": "https://updated.com", "short_name": "updated"}

            response = await client.put(f"/api/links/{link.id}", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["original_url"] == payload["original_url"]
            assert data["short_name"] == payload["short_name"]

            db_session.refresh(link)
            assert link.original_url == payload["original_url"]
            assert link.short_name == payload["short_name"]

        async def test_returns_404_for_unknown_link(self, client: AsyncClient) -> None:
            payload = {"original_url": "https://updated.com", "short_name": "updated"}

            response = await client.put(f"/api/links/{UNKNOWN_LINK_ID}", json=payload)

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

        async def test_rejects_short_name_of_another_link(
            self, client: AsyncClient, link: URL, create_link: Callable[..., URL]
        ) -> None:
            other_link = create_link(
                original_url="https://google.com", short_name="google"
            )
            payload = {
                "original_url": "https://updated.com",
                "short_name": other_link.short_name,
            }

            response = await client.put(f"/api/links/{link.id}", json=payload)

            assert response.status_code == 400
            assert "already exists" in response.json()["detail"]

        async def test_keeps_own_short_name(
            self, client: AsyncClient, link: URL
        ) -> None:
            payload = {
                "original_url": "https://updated.com",
                "short_name": link.short_name,
            }

            response = await client.put(f"/api/links/{link.id}", json=payload)

            assert response.status_code == 200
            assert response.json()["short_name"] == link.short_name

    class TestDelete:
        async def test_removes_link(
            self, client: AsyncClient, db_session: Session, link: URL
        ) -> None:
            link_id = link.id

            response = await client.delete(f"/api/links/{link_id}")

            assert response.status_code == 204
            assert response.content == b""
            assert db_session.get(URL, link_id) is None

        async def test_returns_404_for_unknown_link(self, client: AsyncClient) -> None:
            response = await client.delete(f"/api/links/{UNKNOWN_LINK_ID}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]


class TestRedirect:
    """Ресурс /r/{short_name}"""

    async def test_redirects_to_original_url(
        self, client: AsyncClient, link: URL
    ) -> None:
        response = await client.get(f"/r/{link.short_name}", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == link.original_url

    async def test_returns_404_for_unknown_short_name(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/r/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
