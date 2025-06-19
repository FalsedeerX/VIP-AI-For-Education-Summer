# test_database_agent.py
'''
import os
import uuid
import pytest

from dotenv import load_dotenv

# Import the class under test:
from database_async import DatabaseAgent

#
#  ─── TEST FIXTURE TO PROVIDE A DatabaseAgent ─────────────────────────────────
#
@pytest.fixture(scope="module")
def db_agent():
    agent = DatabaseAgent()

    yield agent

#
#  ─── HELPERS ──────────────────────────────────────────────────────────────────
#
def random_credentials():
    """
    Return a tuple (username, email, password) guaranteed to be unique-ish.
    """
    suffix = uuid.uuid4().hex[:8]
    return (
        f"testuser_{suffix}",
        f"testemail_{suffix}@example.com",
        "Password123!"
    )


#
#  ─── TESTS FOR USER METHODS ────────────────────────────────────────────────────
#
@pytest.mark.asyncio
async def test_register_get_and_delete_user(db_agent):
    # 1) Create a new random user
    username, email, password = random_credentials()

    # register_user should return True the first time
    assert await db_agent.register_user(username, email, password)

    # register_user a second time with same username/email should return False
    assert not await db_agent.register_user(username, email, password)

    # get_user_id should now return a valid int (the new user's ID)
    user_id = await db_agent.get_user_id(username)
    assert isinstance(user_id, int)

    # verify_user with wrong password => False
    assert not await db_agent.verify_user(username, "WrongPassword!")

    # verify_user with correct password => True
    assert await db_agent.verify_user(username, password)

    # delete_user should return True for existing user
    assert await db_agent.delete_user(username)

    # delete_user a second time (user no longer exists) => False
    assert not await db_agent.delete_user(username)

    # get_user_id for deleted user => None
    assert await db_agent.get_user_id(username) is None

    # verify_user for deleted user => False
    assert not await db_agent.verify_user(username, password)


#
#  ─── TESTS FOR FOLDER-RELATED METHODS ──────────────────────────────────────────
#
@pytest.mark.asyncio
async def test_create_get_and_delete_folder(db_agent):
    # 1) Create a fresh user to own folders
    username, email, password = random_credentials()
    assert await db_agent.register_user(username, email, password)
    user_id = await db_agent.get_user_id(username)
    assert isinstance(user_id, int)

    # 2) No folders exist yet for this new user
    assert await db_agent.get_folders(user_id) is None

    # 3) create_folder returns the new folder ID
    folder_label = "MyTestFolder"
    folder_id = await db_agent.create_folder(folder_label, user_id)
    assert isinstance(folder_id, int)

    # 4) Now get_folders should return a dict {"MyTestFolder": []}
    folders = await db_agent.get_folders(user_id)  # notice get_folders takes owner_id as str
    assert isinstance(folders, dict)
    assert folder_label in folders
    assert folders[folder_label] == []  # no chats linked yet

    # 5) Deleting a folder that has no child links should succeed
    assert await db_agent.delete_folder(user_id, folder_id)

    # 6) Deleting same folder again => False
    assert not await db_agent.delete_folder(user_id, folder_id)

    # 7) Cleanup: delete the user
    assert await db_agent.delete_user(username)


@pytest.mark.asyncio
async def test_delete_folder_with_links(db_agent):
    """
    Test that delete_folder first removes chat_folder_link rows before deleting the folder.
    We will:
      - create user
      - create folder
      - create a chat (belonging to same user)
      - call organize_chat to link chat → folder
      - then call delete_folder (should remove link and folder)
    """
    # a) Set up a user
    username, email, password = random_credentials()
    assert await db_agent.register_user(username, email, password)
    user_id = await db_agent.get_user_id(username)
    assert isinstance(user_id, int)

    # b) Create a folder
    folder_label = "FolderWithLink"
    folder_id = await db_agent.create_folder(folder_label, user_id)
    assert isinstance(folder_id, int)

    # c) Create a chat
    chat_title = "ChatForLink_" + uuid.uuid4().hex[:4]
    chat_id = await db_agent.create_chat(user_id, chat_title)

    # d) organize_chat should return True (link chat → folder)
    assert await db_agent.organize_chat(chat_id, folder_label)

    # e) Now get_folders should show that folder has 1 chat_id
    folders_map = await db_agent.get_folders(user_id)
    assert folder_label in folders_map
    assert chat_id in folders_map[folder_label]

    # f) delete_folder should remove both the link row and the folder
    assert await db_agent.delete_folder(user_id, folder_id)

    # g) After deletion, get_folders should return None (no folders)
    assert await db_agent.get_folders(user_id) is None

    # h) Cleanup: delete chat and user
    assert await db_agent.delete_chat(chat_id)
    assert await db_agent.delete_user(username)


#
#  ─── TESTS FOR CHAT-RELATED METHODS ────────────────────────────────────────────
#
@pytest.mark.asyncio
async def test_create_log_get_and_delete_chat(db_agent):
    """
    1) Create a user
    2) Create a chat
    3) Log several messages
    4) Retrieve get_chat_history and verify correct order/values
    5) Delete the chat (should also delete its messages)
    """
    # 1) Create a user
    username, email, password = random_credentials()
    assert await db_agent.register_user(username, email, password)
    user_id = await db_agent.get_user_id(username)
    assert isinstance(user_id, int)

    # 2) Create a chat
    chat_title = "ChatHistoryTest_" + uuid.uuid4().hex[:4]
    chat_id = await db_agent.create_chat(user_id, chat_title)
    assert isinstance(chat_id, str)

    # 3) Log two messages under that chat
    assert await db_agent.log_chat(chat_id, str(user_id), "First message")
    assert await db_agent.log_chat(chat_id, str(user_id), "Second message")

    # 4) get_chat_history must return a list of dicts in chronological order
    history = await db_agent.get_chat_history(chat_id)
    assert isinstance(history, list)
    # Expect exactly 2 rows, each a dict with keys "user_id", "message", "created_at"
    assert len(history) == 2
    assert all(isinstance(row, dict) for row in history)
    assert history[0]["message"] == "First message"
    assert history[1]["message"] == "Second message"
    assert history[0]["user_id"] == user_id
    assert history[1]["user_id"] == user_id

    # 5) Deleting the chat should succeed
    assert await db_agent.delete_chat(chat_id)

    # 6) Now get_chat_history(chat_id) should return None, since the chat no longer exists
    assert await db_agent.get_chat_history(chat_id) is None

    # 7) Cleanup: delete user
    assert await db_agent.delete_user(username)


@pytest.mark.asyncio
async def test_organize_chat_bad_inputs(db_agent):
    """
    Test that organize_chat returns False for invalid inputs:
      - invalid UUID
      - nonexistent folder name
    """
    # invalid UUID format
    assert not await db_agent.organize_chat("not-a-uuid", "SomeFolder")

    # nonexistent folder
    username, email, password = random_credentials()
    assert await db_agent.register_user(username, email, password)
    user_id = await db_agent.get_user_id(username)
    folder_label = "Folder_DoesNotExist"
    # Since no folder "Folder_DoesNotExist" exists, this must return False
    assert not await db_agent.organize_chat(str(uuid.uuid4()), folder_label)

    # Cleanup: delete user
    assert await db_agent.delete_user(username)


#
#  ─── TEST FOR get_folders INVALID owner_id ─────────────────────────────────────
#
@pytest.mark.asyncio
async def test_get_folders_invalid_owner(db_agent):
    # Passing a non-integer string should return None
    assert await db_agent.get_folders(11111) is None


#
#  ─── TEST FOR verify_user_nonexistent ─────────────────────────────────────────
#
@pytest.mark.asyncio
async def test_verify_user_nonexistent(db_agent):
    # If username doesn’t exist at all, verify_user returns False
    assert not await db_agent.verify_user("definitely_not_a_real_user", "any_password")


#
#  ─── TEST FOR get_chat_history_invalid_uuid ────────────────────────────────────
#
@pytest.mark.asyncio
async def test_get_chat_history_invalid_uuid(db_agent):
    # Invalid UUID should return None
    assert await db_agent.get_chat_history("invalid-uuid-format") is None
'''