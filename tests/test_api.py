from app.models import URL


class TestingPingAPI:
    async def test_ping_api(self, test_client):
        response = await test_client.get("/ping")
        assert response.status_code == 200
        assert response.json() == "pong"


class TestingGetLinksAPI:
    """Тесты для эндпоинта GET /links"""

    async def test_get_links_empty_list(self, test_client):
        """Тест получения пустого списка ссылок"""
        response = await test_client.get("/api/links")

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_links_with_data(self, test_client, mock_url_repository):
        """Тест получения списка ссылок с данными"""

        test_urls = [
            URL(id=1, original_url="https://example.com", short_name="example"),
            URL(id=2, original_url="https://google.com", short_name="google"),
        ]

        mock_url_repository.get_all.return_value = test_urls
        mock_url_repository.get_total_count.return_value = 2

        response = await test_client.get("/api/links")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["short_name"] == "example"
        assert data[0]["original_url"] == "https://example.com"
        assert data[1]["short_name"] == "google"
        assert data[1]["original_url"] == "https://google.com"

    async def test_get_links_with_pagination(self, test_client, mock_url_repository):
        """Тест получения списка ссылок с пагинацией"""

        # Создаем 15 тестовых URL
        test_urls = [
            URL(id=i, original_url=f"https://example{i}.com", short_name=f"example{i}")
            for i in range(1, 16)
        ]

        # Возвращаем первые 10 записей (индексы 0-9)
        mock_url_repository.get_all.return_value = test_urls[:10]
        mock_url_repository.get_total_count.return_value = 15

        response = await test_client.get("/api/links?range=[0,10]")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

        # Проверяем заголовок Content-Range
        assert "Content-Range" in response.headers
        assert response.headers["Content-Range"] == "links 0-9/15"

        # Проверяем первую и последнюю запись
        assert data[0]["id"] == 1
        assert data[0]["short_name"] == "example1"
        assert data[9]["id"] == 10
        assert data[9]["short_name"] == "example10"

    async def test_get_links_pagination_empty_range(
        self, test_client, mock_url_repository
    ):
        """Тест пагинации с пустым диапазоном (за пределами данных)"""

        # Возвращаем пустой список
        mock_url_repository.get_all.return_value = []
        mock_url_repository.get_total_count.return_value = 10

        response = await test_client.get("/api/links?range=[20,30]")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        # Проверяем заголовок Content-Range для пустого результата
        assert "Content-Range" in response.headers
        assert response.headers["Content-Range"] == "links 20-20/10"

    async def test_get_links_pagination_without_range(
        self, test_client, mock_url_repository
    ):
        """Тест пагинации без указания range (должны использоваться значения по умолчанию)"""

        test_urls = [
            URL(id=i, original_url=f"https://example{i}.com", short_name=f"example{i}")
            for i in range(1, 6)
        ]

        mock_url_repository.get_all.return_value = test_urls
        mock_url_repository.get_total_count.return_value = 5

        response = await test_client.get("/api/links")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Проверяем заголовок Content-Range
        assert "Content-Range" in response.headers
        assert response.headers["Content-Range"] == "links 0-4/5"


class TestingGetLinkAPI:
    """Тесты для эндпоинта GET /links/{link_id}"""

    async def test_get_link_success(self, test_client, mock_url_repository):
        """Тест успешного получения ссылки по ID"""

        test_url = URL(id=1, original_url="https://example.com", short_name="example")
        mock_url_repository.get_by_id.return_value = test_url

        response = await test_client.get("/api/links/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["short_name"] == "example"
        assert data["original_url"] == "https://example.com"

    async def test_get_link_not_found(self, test_client, mock_url_repository):
        """Тест получения несуществующей ссылки"""
        mock_url_repository.get_by_id.return_value = None

        response = await test_client.get("/api/links/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestingCreateLinkAPI:
    """Тесты для эндпоинта POST /links"""

    async def test_create_link_success(self, test_client, mock_url_repository):
        """Тест успешного создания ссылки"""

        url_data = {"original_url": "https://example.com", "short_name": "example"}

        created_url = URL(
            id=1, original_url="https://example.com", short_name="example"
        )
        mock_url_repository.get_by_short_name.return_value = None
        mock_url_repository.create.return_value = created_url

        response = await test_client.post("/api/links", json=url_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["short_name"] == "example"
        assert data["original_url"] == "https://example.com"

    async def test_create_link_missing_short_name(self, test_client):
        """Тест создания ссылки без short_name"""
        url_data = {"original_url": "https://example.com", "short_name": ""}

        response = await test_client.post("/api/links", json=url_data)

        assert response.status_code == 400
        assert "short_name" in response.json()["detail"]

    async def test_create_link_duplicate_short_name(
        self, test_client, mock_url_repository
    ):
        """Тест создания ссылки с уже существующим short_name"""

        url_data = {"original_url": "https://example.com", "short_name": "example"}

        existing_url = URL(id=1, original_url="https://other.com", short_name="example")
        mock_url_repository.get_by_short_name.return_value = existing_url

        response = await test_client.post("/api/links", json=url_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestingUpdateLinkAPI:
    """Тесты для эндпоинта PUT /links/{link_id}"""

    async def test_update_link_success(self, test_client, mock_url_repository):
        """Тест успешного обновления ссылки"""

        url_data = {"original_url": "https://updated.com", "short_name": "updated"}

        existing_url = URL(
            id=1, original_url="https://example.com", short_name="example"
        )
        updated_url = URL(
            id=1, original_url="https://updated.com", short_name="updated"
        )

        mock_url_repository.get_by_id.return_value = existing_url
        mock_url_repository.get_by_short_name.return_value = None
        mock_url_repository.update.return_value = updated_url

        response = await test_client.put("/api/links/1", json=url_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["short_name"] == "updated"
        assert data["original_url"] == "https://updated.com"

    async def test_update_link_not_found(self, test_client, mock_url_repository):
        """Тест обновления несуществующей ссылки"""
        url_data = {"original_url": "https://updated.com", "short_name": "updated"}

        mock_url_repository.get_by_id.return_value = None

        response = await test_client.put("/api/links/999", json=url_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_link_duplicate_short_name(
        self, test_client, mock_url_repository
    ):
        """Тест обновления ссылки с уже существующим short_name"""

        url_data = {"original_url": "https://updated.com", "short_name": "google"}

        existing_url = URL(
            id=1, original_url="https://example.com", short_name="example"
        )
        other_url = URL(id=2, original_url="https://google.com", short_name="google")

        mock_url_repository.get_by_id.return_value = existing_url
        mock_url_repository.get_by_short_name.return_value = other_url

        response = await test_client.put("/api/links/1", json=url_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_update_link_same_short_name(self, test_client, mock_url_repository):
        """Тест обновления ссылки с тем же short_name"""

        url_data = {"original_url": "https://updated.com", "short_name": "example"}

        existing_url = URL(
            id=1, original_url="https://example.com", short_name="example"
        )
        updated_url = URL(
            id=1, original_url="https://updated.com", short_name="example"
        )

        mock_url_repository.get_by_id.return_value = existing_url
        mock_url_repository.get_by_short_name.return_value = existing_url
        mock_url_repository.update.return_value = updated_url

        response = await test_client.put("/api/links/1", json=url_data)

        assert response.status_code == 200
        data = response.json()
        assert data["short_name"] == "example"


class TestingDeleteLinkAPI:
    """Тесты для эндпоинта DELETE /links/{link_id}"""

    async def test_delete_link_success(self, test_client, mock_url_repository):
        """Тест успешного удаления ссылки"""
        mock_url_repository.delete.return_value = True

        response = await test_client.delete("/api/links/1")

        assert response.status_code == 204
        assert response.content == b""

    async def test_delete_link_not_found(self, test_client, mock_url_repository):
        """Тест удаления несуществующей ссылки"""
        mock_url_repository.delete.return_value = False

        response = await test_client.delete("/api/links/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestingRedirectAPI:
    """Тесты для эндпоинта GET /r/{short_name}"""

    async def test_redirect_success(self, test_client, mock_url_repository):
        """Тест успешного редиректа"""

        test_url = URL(id=1, original_url="https://example.com", short_name="example")
        mock_url_repository.get_by_short_name.return_value = test_url

        response = await test_client.get("/r/example", follow_redirects=False)

        assert response.status_code == 307  # Temporary Redirect
        assert response.headers["location"] == "https://example.com"

    async def test_redirect_not_found(self, test_client, mock_url_repository):
        """Тест редиректа с несуществующим short_name"""
        mock_url_repository.get_by_short_name.return_value = None

        response = await test_client.get("/r/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
