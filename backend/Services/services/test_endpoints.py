import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

# Replace these with your actual service paths
from services.chat_services import router as chat_router
from services.user_services import router as user_router
from services.folder_services import router as folder_router

# Setup FastAPI app
app = FastAPI()
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(folder_router)

# Sample payloads
sample_user = {"username": "testuser1", "email": "test1@example.com", "password": "securepassword11"}
sample_chat = {"user_id": 1, "title": "Test Chat", "message": "Hello"}
sample_folder = {"name": "Test Folder", "owner_id": 1}
sample_folder_update = {"chat_id": 1, "folder_name": "Test Folder"}


@pytest.mark.asyncio
async def test_user_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/users/", json=sample_user)
        print(res.json())
        assert res.status_code == 201
        user_id = res.json()

        res = await ac.get(f"/users/id/{sample_user['username']}")
        assert res.status_code == 200

        res = await ac.get(f"/users/{user_id}", json={"user_id": user_id, "password": sample_user["password"]})
        assert res.status_code == 200

        res = await ac.delete(f"/users/delete/{user_id}", json={"username": sample_user["username"]})
        assert res.status_code in [204, 404]


@pytest.mark.asyncio
async def test_chat_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/chats/chat/", json=sample_chat)
        assert res.status_code == 201
        chat_id = res.json()

        res = await ac.get(f"/chats/chat/{chat_id}")
        assert res.status_code in [200, 404]

        res = await ac.put(f"/chats/chat/{chat_id}", json=sample_chat)
        assert res.status_code in [204, 404]

        res = await ac.delete(f"/chats/chat/{chat_id}")
        assert res.status_code in [204, 404]


@pytest.mark.asyncio
async def test_folder_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/folders/folders/", json=sample_folder)
        assert res.status_code == 201
        folder_id = res.json()

        res = await ac.get(f"/folders/folders/{sample_folder['owner_id']}")
        assert res.status_code in [200, 404]

        res = await ac.put(f"/folders/folders/{folder_id}", json=sample_folder_update)
        assert res.status_code in [204, 404]

        res = await ac.delete(f"/folders/folders/{folder_id}?owner_id={sample_folder['owner_id']}")
        assert res.status_code in [204, 404]
