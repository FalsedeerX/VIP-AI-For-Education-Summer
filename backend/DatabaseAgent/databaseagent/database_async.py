# database_async.py
import os
import uuid
import psycopg
import asyncio
from dotenv import load_dotenv
from psycopg.rows import dict_row
from argon2 import PasswordHasher
from psycopg import AsyncConnection
from typing import Any, Dict, List, Optional
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


    async def get_username(self, user_id: str) -> Optional[str]:
        """Fetch user username by id."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute("SELECT username FROM users WHERE id = %s;", (user_id,))
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


    async def get_chats(self, folder_id: int) -> dict[str, str]:
        """ Get a list of chat IDs of a speicifc folder_id. 
            Return type: <chat-title, chat-id> """
        conn = await get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                    """ SELECT c.title, c.id FROM chat_folder_link AS l 
                        JOIN chats as c ON c.id = l.chat_id 
                        WHERE l.folder_id = %s """,
                    (folder_id,)
                )
            rows = await cur.fetchall()

        # parse the returned results
        return {row["title"]: str(row["id"]) for row in rows}


    async def organize_chat(self, chat_id: str, folder_id: int) -> bool:
        """ Link a chat UUID to a folder label."""
        # Validate UUID
        try:
            uid = uuid.UUID(chat_id)
        except ValueError:
            return False
        conn = await get_connection()
        async with conn.cursor() as cur:
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
            return []

        conn = await get_connection()
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT user_id, message, created_at FROM chat_messages WHERE chat_id = %s ORDER BY created_at;",
                (uid,)
            )
            rows = await cur.fetchall()
        return rows if rows else []


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


    async def get_chat_owner(self, chat_id: str) -> int:
        """ Get the owner of a specific chat. Returns -1 if chat_id DNE. """
        try:
            uid = uuid.UUID(chat_id)
        except ValueError:
            return -1

        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT user_id FROM chats WHERE id = %s;",
                (uid,)
            )
            row = await cur.fetchone()
        
        if row: return row[0]
        else: return -1


    async def get_folder_owner(self, folder_id: int) -> int:
        """ Get the owner of a specific folder. Returns -1 if folder_id DNE. """
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT user_id FROM folders WHERE id = %s;",
                (folder_id,)
            )
            row = await cur.fetchone()
        
        if row: return row[0]
        else: return -1


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


    async def create_folder(self, name: str, course_id: int, user_id: int) -> int:
        """Create a new folder for a user; return the new folder's id."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO folders (label, course_id, user_id) VALUES (%s, %s, %s) RETURNING id;",
                (name, course_id, user_id)
            )
            row = await cur.fetchone()
        await conn.commit()
        return row[0] if row else -1


    async def delete_folder(self, folder_id: int) -> bool:
        """ Delete a folder and its links for a user. """
        conn = await get_connection()
        async with conn.cursor() as cur:
            # remove the chat contained inside the folder
            await cur.execute(
                    """ DELETE FROM chats
                        WHERE id IN (
                            SELECT chat_id FROM chat_folder_link WHERE folder_id = %s
                        );""",
                    (folder_id,)
                )

            # remove the actual folder
            await cur.execute(
                    "DELETE FROM folders WHERE id = %s RETURNING id;",
                    (folder_id,)
                )
            deleted = await cur.fetchone()

        if not deleted: return False
        await conn.commit()
        return True


    async def get_courses(self, user_id: int) -> dict[str, list[int]]:
        """ Return a dictonary of course id and the folder id in each entry.
            <course-name>: [folder_ids] """
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT c.title, f.id FROM folders AS f
                   JOIN courses AS c ON f.course_id = c.id WHERE f.user_id = %s;""", 
                (user_id,)
            )
            rows = await cur.fetchall()

        result = {}
        for course_title, folder_id in rows:
            result.setdefault(course_title, []).append(folder_id)
        return result


    async def delete_course(self, course_id: int) -> bool:
        """ Delete a course and all object which is referencing it. """
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                    "DELETE FROM courses WHERE id = %s",
                    (course_id,)
                )
            rows = cur.rowcount

        await conn.commit()
        return rows > 0


    async def create_course(self, course_code: str, course_title: str|None = None) -> int:
        """ Create a new course entry. On failure returns -1 """
        conn = await get_connection()
        async with conn.cursor() as cur:
            if course_title:
                await cur.execute(
                        "INSERT INTO courses (code, title) VALUES (%s, %s) RETURNING id;",
                        (course_code, course_title)
                    )
            else:
                await cur.execute(
                        "INSERT INTO courses (code) VALUES (%s) RETURNING ID;",
                        (course_code,)
                    )

            row = await cur.fetchone()
        
        await conn.commit()
        return row[0] if row else -1


    async def organize_folder(self, folder_id: int, course_id: int) -> bool:
        """Update folder's course_id only if course exists and folder is valid."""
        conn = await get_connection()
        async with conn.cursor() as cur:
            # check whether the coruse exist
            await cur.execute(
                    "SELECT 1 FROM courses WHERE id = %s;", 
                    (course_id,)
                )
            if not await cur.fetchone(): return False

            # update folder
            await cur.execute(
                    "UPDATE folders SET course_id = %s WHERE id = %s RETURNING id; ", 
                    (course_id, folder_id)
                )
            status = await cur.fetchone()

        await conn.commit()
        return status is not None
    
    async def add_course(self, user_id: int, course_code: str) -> bool:
        """ Add a course to a user's list of courses. """
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id FROM courses WHERE code = %s;", 
                (course_code,)
            )
            row = await cur.fetchone()
            if not row:
                return False
            course_id = row[0]

            await cur.execute(
                """
                UPDATE users
                   SET course_ids = array_append(course_ids, %s)
                 WHERE id = %s;
                """,
                (course_id, user_id)
            )
        await conn.commit()
        return True
    
    async def delete_user_courses(self, user_id: int, course_code: str) -> bool:
        """ Remove a course from a user's list of courses. """
        conn = await get_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id FROM courses WHERE code = %s;", 
                (course_code,)
            )
            row = await cur.fetchone()
            if not row:
                return False
            course_id = row[0]

            await cur.execute(
                """
                UPDATE users
                   SET course_ids = array_remove(course_ids, %s)
                 WHERE id = %s;
                """,
                (course_id, user_id)
            )
        await conn.commit()
        return True
    




if __name__ == "__main__":
    agent = DatabaseAgent()
    data = asyncio.run(agent.get_courses(6))
    print(data)