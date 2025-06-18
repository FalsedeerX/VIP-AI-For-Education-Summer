import uuid
from typing import Any
from tinydb import TinyDB, Query
from tinydb.operations import set
from datetime import datetime, timedelta, UTC


class DatabaseAgent:
	def __init__(self, database):
		self.db = TinyDB(database)
		self.users = self.db.table("users")
		self.sessions = self.db.table("sessions")
		self.chat_folders = self.db.table("chat_folders")
		self.chat_logs = self.db.table("chat_logs")


	def register_user(self, username: str, email: str, password: str) -> bool:
		""" Create a new entry of user in the database """
		# check for duplciate user
		existing = self.users.search((Query().user_id == username) | (Query().email == email))
		if existing: return False 
		
		# setup the user profile in the database
		doc_id = self.users.insert({"user_id": username, "email": email, "password": password})
		self.chat_folders.insert({"user_id": username, "folders": [{"label": "Assignment 1", "chat_ids": []}, {"label": "Assignment 2", "chat_id": []}]})
		return True


	def delete_user(self, username: str) -> bool:
		""" remove a user entry from the database """
		# check for user existance
		user_entry = self.users.get(Query().user_id == username)
		if not user_entry: return False

		# delete the user account
		self.users.remove(Query().user_id == username)

		# delete all associated session token
		self.sessions.remove(Query().user_id == username)

		# delete chat folders
		self.chat_folders.remove(Query().user_id == username)

		# delete all chat logs created by user
		self.chat_logs.remove(Query().user_id == username)
		return True


	def verify_user(self, username: str, password: str) -> bool:
		""" Verify the password for a user """
		user = self.users.get(Query().user_id == username)
		if not user: return False

		# check if the passwor match
		if user.get("password") == password: return True
		else: return False


	def create_session(self, owner_id: str) -> tuple[str, datetime]|None:
		""" Create an UUID-V4 token for the session, return tuple[token, expiration datetime] """
		# verify whether the user exist before operation
		if not self.users.contains(Query().user_id == owner_id): return None

		# token creation
		session_token = str(uuid.uuid4())

		# make the expire time 2 hours later after the token creation (UTC+0 Zone)
		expiration_time = datetime.now(UTC) + timedelta(hours=2)
		expire = expiration_time.timestamp()

		# insert the entry to the database
		self.sessions.insert({"user_id": owner_id, "token": session_token, "expires_at": expire})
		return session_token, expiration_time


	def terminate_session(self, owner_id: str, token: str) -> bool:
		""" Termiante an UUID-V4 session token of user """
		# check if the user & session exist in the database
		removed_doc_id = self.sessions.remove((Query().user_id == owner_id) & (Query().token == token))
		return True if removed_doc_id else False

	def terminate_all_sessions(self, user_id: str) -> bool:
		""" Remove all session tokens for the given user_id """
		removed = self.sessions.remove(Query().user_id == user_id)
		return bool(removed)

	def verify_session(self, owner_id: str, token: str) -> bool:
		""" Verify a session token of the user """
		# check whether the session exist in the database
		session = self.sessions.get((Query().user_id == owner_id) & (Query().token == token))
		if not session: return False

		# check if session expired
		current = datetime.now(UTC).timestamp()
		return current < session.get("expires_at", 0)


	def get_folders(self, owner_id: str) -> dict[str, list[str]]|None:
		""" Return a list folders name and the chat_ids inside it """
		user_folders = self.chat_folders.get(Query().user_id == owner_id)
		if not user_folders: return None
		folders = user_folders.get("folders", [])
		if not folders: return None
		
		# parse the folder and chat_ids
		result: dict[str, list[str]] = {}
		for folder in folders:
			label = folder.get("label")
			chat_ids = folder.get("chat_ids", [])
			if label: result[label] = chat_ids

		return result


	def organize_chat(self, chat_id: str, folder_name: str) -> bool:
		""" Organize a chat into a speicied folder under the username """
		# receive the owner of the chat
		chat_entry = self.chat_logs.get(Query().chat_id == chat_id)
		if not chat_entry: return False
		owner_id = chat_entry.get("user_id")

		# receive the user's chat folder information
		user_entry = self.chat_folders.get(Query().user_id == owner_id)
		if not user_entry: return False

		# locate the "folders" field
		folders = user_entry.get("folders", [])
		if not folders: return False

		# append the chat_id under the correct label
		for folder in folders:
			if folder.get("label") == folder_name:
				chat_ids = folder.setdefault("chat_ids", [])
				if chat_id not in chat_ids: chat_ids.append(chat_id)
				break

		# update the entry for user
		self.chat_folders.update(set("folders", folders), Query().user_id == owner_id)
		return True


	def get_chat_history(self, chat_id: str) -> list[dict[str, Any]]|None:
		""" Return a list of dictionary for the specified chat log """
		chat_entry = self.chat_logs.get(Query().chat_id == chat_id)
		if not chat_entry: return None
		return chat_entry.get("messages", [])


	def create_chat(self, owner_id: str) -> str:
		""" Create an UUID-V4 chat_id and setup empty entry in `chat_log` table """
		chat_id = str(uuid.uuid4())
		self.chat_logs.insert({"chat_id": chat_id, "user_id": owner_id, "messages": []})
		return chat_id


	def log_chat(self, chat_id: str, sender: str, message: str) -> bool:
		""" Add a new message from sender into the specified chat_id """
		chat_entry = self.chat_logs.get(Query().chat_id == chat_id)
		if not chat_entry: return False

		# construct the new message
		new_message = {
			"timestamp": datetime.now(UTC).timestamp(),
			"sender": sender,
			"message": message
		}

		# insert the new message, update the chat_logs table
		messages = chat_entry.setdefault("messages", [])
		messages.append(new_message)
		self.chat_logs.update(set("messages", messages), Query().chat_id == chat_id)
		return True


	def delete_chat(self, chat_id: str) -> bool:
		""" Delete a chat log based on the chat_id """
		chat_entry = self.chat_logs.get(Query().chat_id == chat_id)
		if not chat_entry: return False

		# get owner of the chat
		owner_id = chat_entry.get("user_id")
		if not owner_id: return False

		# locate the owner's folder
		folders_entry = self.chat_folders.get(Query().user_id == owner_id)
		if not folders_entry: return False
		folders = folders_entry.get("folders", [])

		# remove the taret chat_id from the folder
		for folder in folders:
			chat_ids = folder.get("chat_ids", [])
			if chat_id in chat_ids:
				chat_ids.remove(chat_id)
				self.chat_folders.update(set("folders", folders), Query().user_id == owner_id)

		# delete the chat from chat_logs
		self.chat_logs.remove(Query().chat_id == chat_id)
		return True



if __name__ == "__main__":
	agent = DatabaseAgent("database.json")
	agent.organize_chat("5439494f-b9be-4f81-b242-56eecc8c1841", "Assignment 2")
	print(agent.get_folders("chou610"))