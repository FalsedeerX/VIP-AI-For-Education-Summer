import time
import redis
import threading
from uuid import UUID, uuid4
from ipaddress import _BaseAddress


class SessionManager:
	def __init__(self, db_host: str, db_port: int, db_index: int, db_user: str, db_pass: str):
		self.db = redis.Redis(host=db_host, port=db_port, db=db_index, username=db_user, password=db_pass)
		self.db.ping()


	def assign_token(self, username: str, time_to_live: int) -> UUID:
		""" Assigning authenciated user with an UUID as the session token. """
		return uuid4()


	def verify_token(self, username: str, ip_address: str, token: UUID) -> bool:
		""" Verify whether a certain token expired. """
		return False


	def extend_token(self, token: UUID, extend_seconds: float) -> float:
		""" Extend the user session for a specific amount of time. Returns reamining TTL in seconds. """
		return 0.0


	def purge_token(self, token: UUID) -> bool:
		""" Remove a specific token from a user. """
		return False


	def purge_all_tokens(self, username: str) -> int:
		""" Remove all tokens which belong to a specific user. Return number of session terminated. """
		return 0



class SessionWorker:
	def __init__(self):
		pass


	def start(self):
		""" Start the IDLE cleanup worker & expire cleanup worker in the background. """
		pass


	def stop(self):
		""" Stop all the created thread worker gracefully. """
		pass


	def _idle_cleanup_worker(self):
		""" Scan through the database a few minutes to terminate unactive session token. """
		pass


	def _expire_cleanup_worker(self):
		""" Event callback triggered when a key expired in database. """
		pass



if __name__ == "__main__":
	pass
