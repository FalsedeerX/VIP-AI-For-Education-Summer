import psycopg
from typing import Any
from argon2 import PasswordHasher

DB_PORT = 5432
DB_NAME = "purduegptdb"
DB_HOST = "localhost"
DB_USER = "aesir"
DB_PASSWD = "Dance with devil"


class DatabaseAgent:
	def __init__(self):
		self.conn = psycopg.connect(f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
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
		pass


	def verify_user(self, username: str, password: str) -> bool:
		""" Verify the password for a user """
		pass


	def get_folders(self, owner_id: str) -> dict[str, list[str]]|None:
		""" Return a list folders name and the chat_ids inside it """
		pass


	def organize_chat(self, chat_id: str, folder_name: str) -> bool:
		""" Organize a chat into a speicied folder under the username """
		pass


	def get_chat_history(self, chat_id: str) -> list[dict[str, Any]]|None:
		""" Return a list of dictionary for the specified chat log """
		pass


	def create_chat(self, owner_id: str) -> str:
		""" Create an UUID-V4 chat_id and setup empty entry in `chat_log` table """
		pass


	def log_chat(self, chat_id: str, sender: str, message: str) -> bool:
		""" Add a new message from sender into the specified chat_id """
		pass


	def delete_chat(self, chat_id: str) -> bool:
		""" Delete a chat log based on the chat_id """
		pass



if __name__ == "__main__":
	agent = DatabaseAgent()
	agent.register_user("chen5292", "admin@aurvandill.net", "apple123")