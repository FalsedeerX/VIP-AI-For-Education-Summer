import os
import psycopg
from typing import Any
from dotenv import load_dotenv
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