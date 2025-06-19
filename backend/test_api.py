import pytest
import httpx
from typing import AsyncGenerator
import pytest_asyncio

BASE_URL = "http://127.0.0.1:8000"

# --- Test Data ---
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword"
}
test_user_id = None
test_chat_id = None
test_folder_id = None

# Removed @pytest.fixture(scope="module") as @pytest_asyncio.fixture provides similar functionality for async fixtures.
'''
@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    client = httpx.AsyncClient(base_url=BASE_URL)
    yield client
    await client.aclose()
'''

@pytest_asyncio.fixture  # function-scoped by default
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    # open & close within the same event loop
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client


@pytest.mark.asyncio
class TestUserServices:
    """
    Test cases for the User services.
    """
    async def test_register_user(self, client: httpx.AsyncClient):
        """
        Test user registration.
        """
        global test_user_id
        # First, try to delete the user if they already exist from a previous failed run
        try:
            get_user_response = await client.get(f"/users/id/{test_user['username']}")
            if get_user_response.status_code == 200:
                 existing_user_id = get_user_response.json()
                 # Ensure proper payload for delete if it expects username/password
                 #await client.delete(f"/users/{existing_user_id}", json={"username": test_user["username"], "password": test_user["password"]})
                 await client.request(
                    "DELETE",
                    f"/users/{existing_user_id}",
                    json={"username": test_user["username"],
                          "password": test_user["password"]}
                 )
        except Exception as e:
            # Catch specific exceptions if possible, and log for debugging
            print(f"User deletion pre-check failed (might not exist): {e}")
            pass # User doesn't exist, which is fine

        response = await client.post("/users/register", json=test_user)
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}: {response.text}"
        
        # Get the user ID for subsequent tests
        get_user_response = await client.get(f"/users/id/{test_user['username']}")
        assert get_user_response.status_code == 200, f"Expected status 200 for getting user ID, got {get_user_response.status_code}: {get_user_response.text}"
        test_user_id = get_user_response.json()
        assert isinstance(test_user_id, int), f"Expected int for user ID, got {type(test_user_id)}: {test_user_id}"


    async def test_get_user_id(self, client: httpx.AsyncClient):
        """
        Test fetching a user ID by username.
        """
        # This test relies on test_register_user having run successfully and set test_user_id
        # For independent testing, you might register a user within this test or use a fixture.
        # Given the current structure, if test_register_user fails, this will likely fail too.
        response = await client.get(f"/users/id/{test_user['username']}")
        print(f"YOOOOOOOOOOO Response from /users/id/{test_user['username']}: {response.text}")
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
        assert isinstance(response.json(), int)

    async def test_get_nonexistent_user_id(self, client: httpx.AsyncClient):
        """
        Test fetching a non-existent user ID.
        """
        response = await client.get("/users/id/nonexistentuser")
        assert response.status_code == 404, f"Expected status 404, got {response.status_code}: {response.text}"

    async def test_verify_user(self, client: httpx.AsyncClient):
        """
        Test user verification with the correct password.
        
        global test_user_id
        # In a real test suite, you'd ensure test_user_id is set by a prior step or fixture
        # For now, if tests run out of order, this assert might fail.
        # This is where Pytest fixtures or test dependencies become important.
        if test_user_id is None:
            # Fallback: Try to get user ID if not set by previous test (e.g., if running single test)
            get_user_response = await client.get(f"/users/id/{test_user['username']}")
            if get_user_response.status_code == 200:
                test_user_id = get_user_response.json()
            else:
                pytest.fail("Pre-requisite: test_user_id not set and user not found for verification.")

        login_data = {"username": test_user["username"], "password": test_user["password"]}
        response = await client.post(f"/users/auth/{test_user_id}", json=login_data)
        """

        login_data = {"username": test_user["username"], "password": test_user["password"]}
        response = await client.post(f"/users/auth/{test_user_id}", json=login_data)

        assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
        assert response.json() is True, f"Expected True for successful verification, got {response.json()}"

    async def test_verify_user_incorrect_password(self, client: httpx.AsyncClient):
        """
        Test user verification with an incorrect password.
        
        global test_user_id
        if test_user_id is None:
            # Fallback: Try to get user ID if not set by previous test
            get_user_response = await client.get(f"/users/id/{test_user['username']}")
            if get_user_response.status_code == 200:
                test_user_id = get_user_response.json()
            else:
                pytest.fail("Pre-requisite: test_user_id not set and user not found for incorrect password test.")

        login_data = {"username": test_user["username"], "password": "wrongpassword"}
        response = await client.post(f"/users/auth/{test_user_id}", json=login_data)
        """

        login_data = {"username": test_user["username"], "password": "wrongpassword"}
        response = await client.post("/users/auth/0", json=login_data)
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
        assert response.json() is False, f"Expected False for incorrect password, got {response.json()}"


@pytest.mark.asyncio
class TestChatServices:
    """
    Test cases for the Chat services.
    """
    async def test_create_chat(self, client: httpx.AsyncClient):
        """
        Test creating a new chat.
        """
        global test_chat_id, test_user_id
        if test_user_id is None:
            # Fallback: Try to get user ID if not set by previous test
            get_user_response = await client.get(f"/users/id/{test_user['username']}")
            if get_user_response.status_code == 200:
                test_user_id = get_user_response.json()
            else:
                pytest.fail("Pre-requisite: test_user_id not set and user not found for chat creation.")

        chat_data = {"user_id": test_user_id, "title": "My First Chat"}
        response = await client.post("/chats/create", json=chat_data)
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}: {response.text}"
        test_chat_id = response.json()
        # The comment notes it should be a string (UUID) but response_model is int.
        # This test assumes it will be an int as per the current response.
        assert isinstance(test_chat_id, str), f"Expected int for chat ID, got {type(test_chat_id)}: {test_chat_id}"


    async def test_log_chat_message(self, client: httpx.AsyncClient):
        """
        Test logging a message to a chat.
        """
        global test_chat_id, test_user_id
        # Similar fallbacks for test_chat_id and test_user_id if not set
        if test_user_id is None or test_chat_id is None:
            pytest.fail("Pre-requisites: test_user_id and test_chat_id not set for logging message.")

        message_data = {"user_id": test_user_id, "message": "Hello, world!"}
        response = await client.put(f"/chats/{test_chat_id}", json=message_data)
        assert response.status_code == 204, f"Expected status 204, got {response.status_code}: {response.text}"

    async def test_get_chat_message(self, client: httpx.AsyncClient):
        """
        Test fetching chat history.
        """
        global test_chat_id
        if test_chat_id is None:
            pytest.fail("Pre-requisite: test_chat_id not set for getting chat message.")

        response = await client.get(f"/chats/{test_chat_id}")
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
        chat_history = response.json()
        assert len(chat_history) > 0, "Chat history should not be empty"
        assert chat_history[0]["message"] == "Hello, world!", "First message should be 'Hello, world!'"
        assert chat_history[0]["user_id"] == test_user_id, f"First message should be from user {test_user_id}, got {chat_history[0]['user_id']}"

    async def test_get_nonexistent_chat(self, client: httpx.AsyncClient):
        """
        Test fetching a non-existent chat.
        """
        response = await client.get("/chats/0")
        assert response.status_code == 404, f"Expected status 404, got {response.status_code}: {response.text}"

@pytest.mark.asyncio
class TestFolderServices:
    """
    Test cases for the Folder services.
    """
    async def test_create_folder(self, client: httpx.AsyncClient):
        """
        Test creating a new folder.
        """
        global test_folder_id, test_user_id
        if test_user_id is None:
            get_user_response = await client.get(f"/users/id/{test_user['username']}")
            if get_user_response.status_code == 200:
                test_user_id = get_user_response.json()
            else:
                pytest.fail("Pre-requisite: test_user_id not set and user not found for folder creation.")

        folder_data = {"owner_id": test_user_id, "name": "My Test Folder"}
        response = await client.post("/folders/create", json=folder_data)
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}: {response.text}"
        test_folder_id = response.json()
        assert isinstance(test_folder_id, int), f"Expected int for folder ID, got {type(test_folder_id)}: {test_folder_id}"

    async def test_get_folders(self, client: httpx.AsyncClient):
        """
        Test fetching folders for a user.
        """
        global test_user_id
        if test_user_id is None:
            get_user_response = await client.get(f"/users/id/{test_user['username']}")
            if get_user_response.status_code == 200:
                test_user_id = get_user_response.json()
            else:
                pytest.fail("Pre-requisite: test_user_id not set and user not found for getting folders.")

        response = await client.get(f"/folders/{test_user_id}")
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
        folders = response.json()
        assert "My Test Folder" in folders, f"Expected 'My Test Folder' in folders, got {folders}"

    async def test_update_folder(self, client: httpx.AsyncClient):
        """
        Test organizing a chat into a folder.
        """
        global test_folder_id, test_chat_id
        # Robustness check for IDs
        if test_folder_id is None or test_chat_id is None:
            pytest.fail("Pre-requisites: test_folder_id or test_chat_id not set for folder update.")

        # The chat_id should be a UUID string, but create_chat returns an int.
        # This will likely fail until the create_chat response is corrected to a string.
        # For now, we cast it to a string for the payload.
        update_data = {"chat_id": str(test_chat_id), "folder_name": "My Test Folder"}
        response = await client.put(f"/folders/organize/{test_folder_id}", json=update_data)
        assert response.status_code == 204, f"Expected status 204, got {response.status_code}: {response.text}"

    async def test_delete_folder(self, client: httpx.AsyncClient):
        """
        Test deleting a folder.
        """
        global test_folder_id, test_user_id
        if test_folder_id is None or test_user_id is None:
            pytest.fail("Pre-requisites: test_folder_id or test_user_id not set for folder deletion.")

        #response = await client.delete(f"/folders/{test_folder_id}?owner_id={test_user_id}")
        response = await client.request(
        "DELETE",
        f"/folders/{test_folder_id}",
        params={"owner_id": test_user_id}
        )
        assert response.status_code == 204, f"Expected status 204, got {response.status_code}: {response.text}"

@pytest.mark.asyncio
class TestCleanup:
    """
    Clean up created test data.
    """
    async def test_delete_chat(self, client: httpx.AsyncClient):
        """
        Test deleting a chat.
        """
        global test_chat_id
        if test_chat_id is None:
            pytest.fail("Pre-requisite: test_chat_id not set for chat deletion.")

        response = await client.delete(f"/chats/{test_chat_id}")
        assert response.status_code == 204, f"Expected status 204, got {response.status_code}: {response.text}"

    async def test_delete_user(self, client: httpx.AsyncClient):
        """
        Test deleting a user.
        """
        global test_user_id
        if test_user_id is None:
            pytest.fail("Pre-requisite: test_user_id not set for user deletion.")

        delete_data = {"username": test_user["username"], "password": test_user["password"]}
        #response = await client.delete(f"/users/{test_user_id}", json=delete_data)
        response = await client.request(
        "DELETE",
        f"/users/{test_user_id}",
        json=delete_data
        )
        assert response.status_code == 204, f"Expected status 204, got {response.status_code}: {response.text}"

