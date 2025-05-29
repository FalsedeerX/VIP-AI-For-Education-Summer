import uuid
from typing import Any
from tinydb import TinyDB, Query
from tinydb.operations import set
from datetime import datetime, timedelta, UTC


class DatabaseAgent:
	def __init__(self, database):
		pass


	def register_user(self, username: str, email: str, password: str) -> bool:
		""" Create a new entry of user in the database """
		pass


	def delete_user(self, username: str) -> bool:
		""" remove a user entry from the database """
		pass


	def verify_user(self, username: str, password: str) -> bool:
		""" Verify the password for a user """
		pass


	def create_session(self, owner_id: str) -> tuple[str, datetime]|None:
		""" Create an UUID-V4 token for the session, return tuple[token, expiration datetime] """
		pass


	def terminate_session(self, owner_id: str, token: str) -> bool:
		""" Termiante an UUID-V4 session token of user """
		pass


	def terminate_all_sessions(self, user_id: str) -> bool:
		""" Remove all session tokens for the given user_id """
		pass


	def verify_session(self, owner_id: str, token: str) -> bool:
		""" Verify a session token of the user """
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
	pass