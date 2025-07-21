#RUNS OUT OF ORDER AND REQUIRES BACKEND TO BE RUNNING AND NEEDS "secure=False" IN user_services.py

import pytest
import httpx
import pytest_asyncio
from typing import AsyncGenerator

BASE_URL = "http://127.0.0.1:8000"

# --- Test Data ---
test_user = {
    "username": "testuser55",
    "email": "test55@example.com",
    "password": "testpassword55",
    "is_admin": True
}

test_user_id: int = None

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL) as c:
        yield c

@pytest_asyncio.fixture
async def auth_client(client: httpx.AsyncClient) -> AsyncGenerator[httpx.AsyncClient, None]:
    # 1) register (ignore 409 conflict)
    await client.post("/users/register", json=test_user)

    # 2) login
    r = await client.post("/users/auth", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert r.status_code == 200 and r.json() is True

    # 3) fetch current user and store its ID
    global test_user_id
    r = await client.get("/users/me")
    assert r.status_code == 200
    test_user_id = r.json()["id"]

    # now client.cookies contains purduegpt-token
    yield client

@pytest.mark.asyncio
class TestUserServices:
    async def test_register_and_login_and_get_me(self, client: httpx.AsyncClient):
        # register
        r = await client.post("/users/register", json=test_user)
        assert r.status_code == 201

        # login
        cred = {"username": test_user["username"], "password": test_user["password"]}
        r = await client.post("/users/auth", json=cred)
        assert r.status_code == 200 and r.json() is True

        # get current user
        r = await client.get("/users/me")
        assert r.status_code == 200
        body = r.json()
        assert body["username"] == test_user["username"]
        assert isinstance(body["id"], int)

    async def test_getcourses_empty(self, auth_client: httpx.AsyncClient):
        # should be empty list at start
        r = await auth_client.get("/users/getcourses")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

@pytest.mark.asyncio
class TestChatServices:
    async def test_create_and_get_and_delete_chat(self, auth_client: httpx.AsyncClient):
        global test_chat_id, test_user_id
        assert test_user_id is not None, "User must be created first"

        # create chat
        chat_payload = {"title": "My First Chat"}
        r = await auth_client.post("/chats/create", json=chat_payload)
        assert r.status_code == 201
        test_chat_id = r.json()
        assert isinstance(test_chat_id, str)

        # get random (should return our chat id or another)
        r = await auth_client.get("/chats/random")
        assert r.status_code == 200
        assert isinstance(r.json(), (str, type(None)))

        # get owner
        r = await auth_client.get(f"/chats/owner/{test_chat_id}")
        assert r.status_code == 200
        assert r.json() == {"owner_id": test_user_id}

        # get messages (empty at start)
        r = await auth_client.get(f"/chats/{test_chat_id}")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

        # delete chat
        r = await auth_client.delete(f"/chats/delete/{test_chat_id}")
        assert r.status_code == 200 and r.json() is True

        # now fetching it returns 404
        r = await auth_client.get(f"/chats/{test_chat_id}")
        assert r.status_code == 404

@pytest.mark.asyncio
class TestFolderServices:
    async def test_create_and_get_and_organize_and_delete_folder(self, auth_client: httpx.AsyncClient):
        global test_folder_id, test_user_id, test_chat_id
        assert test_user_id is not None, "User must be created first"

        # create a course first
        r = await auth_client.post("/courses/create", json={"course_code": "C123", "course_title": "Test Course"})
        assert r.status_code == 200
        test_course_id = r.json()
        assert isinstance(test_course_id, int)


        # re-create a chat to organize
        r = await auth_client.post("/chats/create", json={"title": "Chat for Folder"})
        assert r.status_code == 201
        test_chat_id = r.json()

        # create folder (admin-only)
        folder_payload = {"folder_name": "My Test Folder", "course_id": test_course_id}
        r = await auth_client.post("/folders/create", json=folder_payload)
        assert r.status_code == 201
        test_folder_id = r.json()
        assert isinstance(test_folder_id, int)

        # get folders
        course_folders_payload = {"course_id": test_course_id}
        r = await auth_client.post("/courses/get", json=course_folders_payload)
        assert r.status_code == 200
        folders = r.json()
        assert isinstance(folders, list)
        assert any(folder["folder_id"] == test_folder_id for folder in folders)

        # get chats in folder (empty)
        r = await auth_client.post("/folders", json={"folder_id": test_folder_id})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json() == []

        # organize chat into folder
        organize_payload = {"chat_id": test_chat_id, "folder_id": test_folder_id}
        r = await auth_client.post("/chats/organize", json=organize_payload)
        assert r.status_code == 200 and r.json() is True

        # now /folders returns one chat
        r = await auth_client.post("/folders", json={"folder_id": test_folder_id})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and data[0]["chat_id"] == test_chat_id

        # delete folder
        r = await auth_client.request(
            "DELETE",
            "/folders/delete",
            json={"folder_id": test_folder_id}
        )
        assert r.status_code == 200 and r.json() is True

@pytest.mark.asyncio
class TestCourseServices:
    async def test_create_and_get_and_organize_and_delete_course(self, auth_client: httpx.AsyncClient):
        global test_course_id, test_user_id
        assert test_user_id is not None, "User must be created first"

        # join course
        join_payload = {"course_code": "C123"}
        r = await auth_client.post("/users/joincourse", json=join_payload)
        assert r.status_code == 200 and r.json() is True

        # get user courses
        r = await auth_client.get("/users/getcourses")
        assert r.status_code == 200
        courses = r.json()
        assert isinstance(courses, list)
        assert any(course["title"] == "Test Course" for course in courses)

        # delete course form user list
        delete_payload = {"course_code": "C123"}
        r = await auth_client.post("/users/deletecourse", json=delete_payload)
        assert r.status_code == 200 and r.json() is True
        
        # get user courses
        r = await auth_client.get("/users/getcourses")
        assert r.status_code == 200
        courses = r.json()
        assert isinstance(courses, list)
        assert not any(course["title"] == "Test Course" for course in courses)

        #get user owned courses
        r = await auth_client.get("/courses")
        assert r.status_code == 200
        courses = r.json()
        assert isinstance(courses, dict)
        assert courses == {}

        # delete course
        r = await auth_client.request(
            "DELETE",
            "/courses/delete",
            json={"course_id": 1}
        )
        assert r.status_code == 200 and r.json() is True

        # get user owned courses
        r = await auth_client.get("/courses")
        assert r.status_code == 200
        courses = r.json()
        assert isinstance(courses, dict)
        assert "C123" not in courses


@pytest.mark.asyncio
class TestCleanup:
    async def test_delete_user(self, auth_client: httpx.AsyncClient):
        global test_user_id
        assert test_user_id is not None, "User must be created first"

        # delete user
        r = await auth_client.request(
            "DELETE",
            "/users/delete",
            json={"user_id": test_user_id}
        )
        assert r.status_code == 200 and r.json() is True

        # now /users/me unauthorized
        r = await auth_client.get("/users/me")
        assert r.status_code == 404
