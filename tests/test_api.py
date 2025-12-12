
class TestingPingAPI:
    async def test_ping_api(self, test_client):
        response = await test_client.get("/ping")
        assert response.status_code == 200
        assert response.json() == "pong"