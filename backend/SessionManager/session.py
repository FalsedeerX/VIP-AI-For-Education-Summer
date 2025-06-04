import time
import uuid
import redis


class SessionManager:
	def __init__(self, db_host: str, db_port: int, db_index: int, db_user: str, db_pass: str):
		self.db = redis.Redis(host=db_host, port=db_port, db=db_index, username=db_user, password=db_pass)
		self.db.ping()


	def assign_token(self, username: str, time_to_live: int):
		""" Assigning authenciated user with an UUID as the session token. """
		pass


	def verify_token(self):
		""" Verify whether a certain token expired. """
		pass


	def extend_token(self):
		""" Extend the user session for a specific amount of time. """
		pass


	def purge_token(self):
		""" Remove a specific token from a user. """
		pass


	def purge_all_tokens(self):
		""" Remove all tokens which belong to a specific user. """
		pass



if __name__ == "__main__":
	pass
