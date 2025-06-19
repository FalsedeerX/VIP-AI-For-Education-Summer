# database_async.py
import os
import uuid
import psycopg
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

load_dotenv()
_conn: AsyncConnection | None = None

async def get_connection() -> AsyncConnection:
    global _conn
    if _conn is None:
        _conn = await AsyncConnection.connect(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWD')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        await _conn.execute("SET search_path TO chatbot;")
    return _conn


class DatabaseAgent:
    def __init__(self):
        self.hasher = PasswordHasher()


    async def register_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user entry."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT EXISTS (SELECT 1 FROM users WHERE username = %s OR email = %s);",
                (username, email)
            )
            if (await cur.fetchone())[0]:
                return False
            await cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s);",
                (username, email, self.hasher.hash(password))
            )
        await conn.commit()
        return True


    async def get_user_id(self, username: str) -> Optional[int]:
        """Fetch user ID by username."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            row = await cur.fetchone()
        return row[0] if row else None


    async def delete_user(self, user_id: int) -> bool:
        """Delete user by user ID."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM users WHERE id = %s RETURNING id;",
                (user_id,)
            )
            result = await cur.fetchone()

        if result is None:
            return False

        await conn.commit()
        return True



    async def verify_user(self, username: str, password: str) -> bool:
        """Validate a user's password."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute("SELECT password FROM users WHERE username = %s;", (username,))
            row = await cur.fetchone()
            if not row:
                return False
            hashed = row[0]
        try:
            self.hasher.verify(hashed, password)
            return True
        except VerifyMismatchError:
            return False


    async def get_folders(self, owner_id: int) -> Optional[Dict[str, List[str]]]:
        """Fetch folders and their chat IDs for a user."""

        conn = await get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT id, label FROM folders WHERE user_id = %s;",
                (owner_id,)
            )
            folders = await cur.fetchall()
            if not folders:
                return None
            result: Dict[str, List[str]] = {}
            for f in folders:
                fid = f["id"]
                label = f["label"]
                await cur.execute(
                    "SELECT chat_id FROM chat_folder_link WHERE folder_id = %s;",
                    (fid,)
                )
                links = await cur.fetchall()
                result[label] = [str(r["chat_id"]) for r in links]
        return result


    async def organize_chat(self, chat_id: str, folder_name: str) -> bool:
        """Link a chat UUID to a folder label."""
        # Validate UUID
        try:
            uid = uuid.UUID(chat_id)
        except ValueError:
            return False
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM folders WHERE label = %s;", (folder_name,))
            row = await cur.fetchone()
            if not row:
                return False
            folder_id = row[0]
            await cur.execute(
                "INSERT INTO chat_folder_link (chat_id, folder_id) VALUES (%s, %s);",
                (uid, folder_id)
            )
        await conn.commit()
        return True


    async def get_chat_history(self, chat_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch messages for a chat ordered by timestamp."""
        try:
            uid = uuid.UUID(chat_id)
        except ValueError:
            return None
        conn = await get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT user_id, message, created_at FROM chat_messages WHERE chat_id = %s ORDER BY created_at;",
                (uid,)
            )
            rows = await cur.fetchall()
        return rows if rows else None


    async def create_chat(self, user_id: int, title: str) -> str:
        """Create a new chat and return its UUID string."""
        uid = uuid.uuid4()
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO chats (id, user_id, title) VALUES (%s, %s, %s);",
                (uid, user_id, title)
            )
        await conn.commit()
        return str(uid)


    async def log_chat(self, chat_id: str, sender: str, message: str) -> bool:
        """Append a message to a chat."""
        try:
            uid = uuid.UUID(chat_id)
        except ValueError:
            return False
        try:
            sid = int(sender)
        except ValueError:
            return False
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO chat_messages (user_id, chat_id, message) VALUES (%s, %s, %s);",
                (sid, uid, message)
            )
        await conn.commit()
        return True


    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and related data."""
        try:
            uid = uuid.UUID(chat_id)
        except ValueError:
            return False
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM chat_folder_link WHERE chat_id = %s;",
                (uid,)
            )
            await cur.execute(
                "DELETE FROM chat_messages WHERE chat_id = %s;",
                (uid,)
            )
            await cur.execute(
                "DELETE FROM chats WHERE id = %s RETURNING id;",
                (uid,)
            )
            deleted = await cur.fetchone()
        if not deleted:
            return False
        await conn.commit()
        return True


    async def create_folder(self, name: str, owner_id: int) -> int:
        """Create a new folder for a user; return the new folder's id."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO folders (user_id, label) VALUES (%s, %s) RETURNING id;",
                (owner_id, name)
            )
            row = await cur.fetchone()
        await conn.commit()
        return row[0] if row else -1


    async def delete_folder(self, owner_id: int, folder_id: int) -> bool:
        """Delete a folder and its links for a user."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM chat_folder_link WHERE folder_id = %s;", (folder_id,))
            await cur.execute(
                "DELETE FROM folders WHERE id = %s AND user_id = %s RETURNING id;",
                (folder_id, owner_id)
            )
            deleted = await cur.fetchone()
        if not deleted:
            return False
        await conn.commit()
        return True

