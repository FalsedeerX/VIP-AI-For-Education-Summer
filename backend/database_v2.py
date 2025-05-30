import os
import uuid
import psycopg
from typing import Any
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class DatabaseAgent:
	def __init__(self, db_host: str, db_port: int, db_name: str, db_user: str, db_passwd: str):
		self.conn = psycopg.connect(f"postgresql://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_name}")
		self.conn.execute("SET search_path TO chatbot;")
		self.hasher = PasswordHasher()


	def register_user(self, username: str, email: str, password: str) -> bool:
		""" Create a new entry of user in the database """
		with self.conn.cursor() as cursor:
			cursor.execute("""
				SELECT EXISTS (
					SELECT 1 FROM users WHERE username = %s OR email = %s
				);
				""", (username, email))

			# username or email already exists
			if cursor.fetchone()[0]: return False

			# insert new user
			cursor.execute("""
				INSERT INTO users (username, email, password)
				VALUES (%s, %s, %s)
				""", (username, email, self.hasher.hash(password)))

		self.conn.commit()
		return True


	def delete_user(self, username: str) -> bool:
		""" remove a user entry from the database """
		with self.conn.cursor() as cursor:
			cursor.execute("""
				DELETE FROM users WHERE username = %s
				RETURNING id
				""", (username,))

			# check whether any row is affected
			if cursor.fetchone() is None: return False
		
		self.conn.commit()	
		return True


	def verify_user(self, username: str, password: str) -> bool:
		""" Verify the password for a user """
		with self.conn.cursor() as cursor:
			cursor.execute("""
				SELECT password FROM users WHERE username = %s;
				""", (username,))

			# extract the password and check whether user exist
			row = cursor.fetchone()
			if row is None: return False
			hashed_password = row[0]

			# verify the argon2 hashed password
			try:
				self.hasher.verify(hashed_password, password)
				return True

			except VerifyMismatchError:
				return False


	def get_folders(self, owner_id: str) -> dict[str, list[str]]|None:
		""" Return a list folders name and the chat_ids inside it """
		# Ensure owner_id is an integer
		try:
			user_id = int(owner_id)
		except ValueError:
			return None

		with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
			# Fetch folders for user
			cur.execute(
				"SELECT id, label FROM folders WHERE user_id = %s",
				(user_id,)
			)
			folders = cur.fetchall()
			if not folders:
				return None

			result: dict[str, list[str]] = {}
			for folder in folders:
				cur.execute(
					"SELECT chat_id FROM chat_folder_link WHERE folder_id = %s",
					(folder["id"],)
				)
				links = cur.fetchall()
				chat_ids = [str(link["chat_id"]) for link in links]
				result[folder["label"]] = chat_ids

		return result


	def organize_chat(self, chat_id: str, folder_name: str) -> bool:
		""" Organize a chat into a speicied folder under the username """
		pass


	def get_chat_history(self, chat_id: str) -> list[dict[str, any]] | None:
		"""Fetch all messages in a chat ordered by timestamp."""
		# Validate chat_id as a UUID string
		try:
			uuid_obj = uuid.UUID(chat_id)
		except ValueError:
			return None

		with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
			cur.execute(
				"SELECT user_id, message, created_at FROM chat_messages WHERE chat_id = %s ORDER BY created_at",
				(uuid_obj,)
			)
			rows = cur.fetchall()
			if not rows:
				return None
			return rows

	def create_chat(self, user_id: int, title: str) -> str:
		"""Creates a new chat record and returns its UUID."""
		chat_id = uuid.uuid4()
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(
					"INSERT INTO chats (id, user_id, title) VALUES (%s, %s, %s)",
					(chat_id, user_id, title)
				)
		return str(chat_id)


	def log_chat(self, chat_id: str, sender: str, message: str) -> bool:
		""" Add a new message from sender into the specified chat_id """
		# Validate chat_id as a UUID string
		try:
			uuid_obj = uuid.UUID(chat_id)
		except ValueError:
			return None
		
		# Validate sender as an integer user_id
		try:
			user_id = int(sender)
		except ValueError:
			return None
		
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(
					"INSERT INTO chat_messages (user_id, chat_id, message) VALUES (%s, %s, %s)",
					(user_id, uuid_obj, message)
				)
		
		return True


	def delete_chat(self, chat_id: str) -> bool:
		# Validate chat_id as a UUID string
		try:
			uuid_obj = uuid.UUID(chat_id)
		except ValueError:
			return None
		
		with self.conn:
			with self.conn.cursor() as cur:
				# Delete messages associated with the chat
				cur.execute(
					"DELETE FROM chat_messages WHERE chat_id = %s",
					(uuid_obj,)
				)

				# Delete the chat itself
				cur.execute(
					"DELETE FROM chats WHERE id = %s RETURNING id",
					(uuid_obj,)
				)
				deleted = cur.fetchone()

				return deleted is not None
		
	
	def create_folder(self, owner_id: int, label: str) -> int:
		"""Create a new folder for a user; return the new folder's id."""
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(
					"INSERT INTO folders (user_id, label) VALUES (%s, %s) RETURNING id",
					(owner_id, label)
				)
				return cur.fetchone()[0]

	def delete_folder(self, owner_id: int, folder_id: int) -> bool:
		"""Delete a folder belonging to the user; return True if deleted."""
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(
					"DELETE FROM folders WHERE id = %s AND user_id = %s RETURNING id",
					(folder_id, owner_id)
				)
				deleted = cur.fetchone()
				return bool(deleted)
			


if __name__ == "__main__":
	load_dotenv()
	db_host = os.getenv("DB_HOST")
	db_port = int(os.getenv("DB_PORT"))
	db_name = os.getenv("DB_NAME")
	db_user = os.getenv("DB_USER")
	db_passwd = os.getenv("DB_PASSWD")

	# connect to the database broker
	agent = DatabaseAgent(db_host, db_port, db_name, db_user, db_passwd)
	agent.register_user("falsedeer", "ani10242048@gmail.com", "password123")
	agent.register_user("chen5292", "admin@aurvandill.net", "apple123")
	
	# attempt to verify the user with password
	status1 = agent.verify_user("falsedeer", "fakepassword")
	print("Verification Attempt on Falsedeer:", status1)
	status2 = agent.verify_user("falsedeer", "password123")
	print("Verification Attempt on Falsedeer:", status2)