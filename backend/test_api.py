import pytest
import httpx
import pytest_asyncio
from typing import AsyncGenerator

BASE_URL = "http://127.0.0.1:8000"

# --- Test Data ---
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "is_admin": True
}
test_user_id: int = None
test_chat_id: str = None
test_folder_id: int = None

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client

@pytest.mark.asyncio
class TestUserServices:
    async def test_register_and_login_and_get_me(self, client: httpx.AsyncClient):
        # register
        r = await client.post("/users/register", json=test_user)
        assert r.status_code == 201, r.text

        # login
        cred = {"username": test_user["username"], "password": test_user["password"]}
        r = await client.post("/users/auth", json=cred)
        assert r.status_code == 200 and r.json() is True

        # get current user
        r = await client.get("/users/me")
        assert r.status_code == 200
        body = r.json()
        assert body["username"] == test_user["username"]
        assert "id" in body and isinstance(body["id"], int)
        global test_user_id
        test_user_id = body["id"]

    async def test_getcourses_empty(self, client: httpx.AsyncClient):
        # should be empty list at start
        r = await client.get("/users/getcourses")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

@pytest.mark.asyncio
class TestChatServices:
    async def test_create_and_get_and_delete_chat(self, client: httpx.AsyncClient):
        global test_chat_id, test_user_id
        assert test_user_id is not None, "User must be created first"

        # create chat
        chat_payload = {"title": "My First Chat"}
        r = await client.post("/chats/create", json=chat_payload)
        assert r.status_code == 201
        test_chat_id = r.json()
        assert isinstance(test_chat_id, str)

        # get random (should return our chat id or another)
        r = await client.get("/chats/random")
        assert r.status_code == 200
        assert isinstance(r.json(), (str, type(None)))

        # get owner
        r = await client.get(f"/chats/owner/{test_chat_id}")
        assert r.status_code == 200
        assert r.json() == {"owner_id": test_user_id}

        # get messages (empty at start)
        r = await client.get(f"/chats/{test_chat_id}")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

        # delete chat
        r = await client.delete(f"/chats/delete/{test_chat_id}")
        assert r.status_code == 200 and r.json() is True

        # now fetching it returns 404
        r = await client.get(f"/chats/{test_chat_id}")
        assert r.status_code == 404

@pytest.mark.asyncio
class TestFolderServices:
    async def test_create_and_get_and_organize_and_delete_folder(self, client: httpx.AsyncClient):
        global test_folder_id, test_user_id, test_chat_id
        assert test_user_id is not None, "User must be created first"

        # re-create a chat to organize
        r = await client.post("/chats/create", json={"title": "Chat for Folder"})
        assert r.status_code == 201
        test_chat_id = r.json()

        # create folder (admin-only)
        folder_payload = {"folder_name": "My Test Folder", "course_id": 0}
        r = await client.post("/folders/create", json=folder_payload)
        assert r.status_code == 201
        test_folder_id = r.json()
        assert isinstance(test_folder_id, int)

        # get chats in folder (empty)
        r = await client.post("/folders", json={"folder_id": test_folder_id})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

        # organize chat into folder
        organize_payload = {"chat_id": test_chat_id, "folder_id": test_folder_id}
        r = await client.post("/chats/organize", json=organize_payload)
        assert r.status_code == 200 and r.json() is True

        # now /folders returns one chat
        r = await client.post("/folders", json={"folder_id": test_folder_id})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and data[0]["chat_id"] == test_chat_id

        # delete folder
        r = await client.delete("/folders/delete", json={"folder_id": test_folder_id})
        assert r.status_code == 200 and r.json() is True

        # cleaning up chat
        r = await client.delete(f"/chats/delete/{test_chat_id}")
        assert r.status_code == 200 and r.json() is True

@pytest.mark.asyncio
class TestCourseServices:
    async def test_create_and_get_and_organize_and_delete_course(self, client: httpx.AsyncClient):
        global test_course_id, test_user_id
        assert test_user_id is not None, "User must be created first"

        # create a course
        r = await client.post("/courses/create", json={"course code": "C123", "course title": "Test Course"})
        assert r.status_code == 201
        test_course_id = r.json()
        assert isinstance(test_course_id, int)

        # create fol

        # get chats in folder (empty)
        r = await client.post("/folders", json={"folder_id": test_folder_id})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

        # organize chat into folder
        organize_payload = {"chat_id": test_chat_id, "folder_id": test_folder_id}
        r = await client.post("/chats/organize", json=organize_payload)
        assert r.status_code == 200 and r.json() is True

        # now /folders returns one chat
        r = await client.post("/folders", json={"folder_id": test_folder_id})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and data[0]["chat_id"] == test_chat_id

        # delete folder
        r = await client.delete("/folders/delete", json={"folder_id": test_folder_id})
        assert r.status_code == 200 and r.json() is True

        # cleaning up chat
        r = await client.delete(f"/chats/delete/{test_chat_id}")
        assert r.status_code == 200 and r.json() is True

@pytest.mark.asyncio
class TestCleanup:
    async def test_delete_user(self, client: httpx.AsyncClient):
        global test_user_id
        assert test_user_id is not None, "User must be created first"

        # delete user
        r = await client.delete("/users/delete", json={"user_id": test_user_id})
        assert r.status_code == 200 and r.json() is True

        # now /users/me unauthorized
        r = await client.get("/users/me")
        assert r.status_code == 401
