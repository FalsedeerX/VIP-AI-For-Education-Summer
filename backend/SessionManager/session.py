import time
import redis
import threading
import ipaddress
from typing import Any
from uuid import UUID, uuid4
from collections.abc import Sequence
from dataclasses import dataclass, field


@dataclass
class ValkeyConfig:
	db_host: str
	db_port: int
	db_index: int = field(default=0)
	db_user: str|None = field(default=None)
	db_pass: str|None = field(default=None)



class SessionManager:
	def __init__(self, config: ValkeyConfig):
		self.db = redis.Redis(host=config.db_host, port=config.db_port, db=config.db_index, 
							  username=config.db_user, password=config.db_pass, decode_responses=True)
		self.db.ping()


	def assign_token(self, username: str, ip_address: str, ttl_seconds: int = 10800) -> UUID|None:
		""" Assigning authenciated user with an UUID as the session token. """
		# validate IP format
		try:
			parsed_ip = ipaddress.ip_address(ip_address)
		except ValueError:
			return None

		# create a new hash entry
		token = uuid4()
		session_key = f"session:{token}"
		session_data = {
			"username": username,
			"ip_address": str(parsed_ip),
			"created_at": str(time.time())
		}

		# insert and set auto-expire
		self.db.hset(session_key, mapping=session_data)
		self.db.expire(session_key, ttl_seconds)
		self.db.zadd(f"user_sessions:{username}", {str(token): time.time()})
		return token


	def verify_token(self, username: str, ip_address: str, token: UUID) -> bool:
		""" Verify whether a certain token expired. """
		# validate IP format
		try:
			parsed_ip = ipaddress.ip_address(ip_address)
		except ValueError:
			return False

		# verify whether the session token exist in DB
		session_key = f"session:{token}"
		if not self.db.exists(session_key): return False

		# compare the metadata to ensure integrity
		username_metadata = self.db.hget(session_key, "username")
		ipaddress_metadata = self.db.hget(session_key, "ip_address")
		if not username_metadata == username and not ipaddress_metadata == ip_address:
			return False

		# update the score in session tracking
		self.db.zadd(f"user_sessions:{username}", {str(token): time.time()})
		return True


	def extend_token(self, token: UUID, extend_seconds: int) -> int:
		""" Extend the user session for a specific amount of time. Returns reamining TTL in seconds. """
		session_key = f"session:{token}"
		ttl = self.db.ttl(session_key)
		if not isinstance(ttl, int): return 0

		# check if the key expired already (-2) or not expirable (-1)
		if ttl <= 0: return 0

		# update the remaining time-to-live
		self.db.expire(session_key, ttl + extend_seconds)
		return ttl + extend_seconds


	def purge_token(self, token: UUID) -> bool:
		""" Remove a specific token from a user. """
		# check whether the key exist in database & username
		session_key = f"session:{token}"
		username = self.db.hget(session_key, "username")
		if not username: return False

		# remove key and untrack session
		self.db.zrem(f"user_sessions:{username}", str(token))
		self.db.delete(session_key)
		return True


	def fetch_active_tokens(self, username: str) -> list[str]|None:
		""" Fetch all active session tokens from a certain user """
		entries = self.db.zrange(f"user_sessions:{username}", 0, -1)
		if not isinstance(entries, Sequence): return None
		if not isinstance(entries[0], str): return None
		return list(entries)


	def purge_all_tokens(self, username: str) -> int:
		""" Remove all tokens which belong to a specific user. Return number of session terminated. """
		return 0



class SessionWorker:
	def __init__(self, config: ValkeyConfig, scan_interval_seconds: int = 60, idle_timeout_seconds: int = 3600):
		self.db = redis.Redis(host=config.db_host, port=config.db_port, db=config.db_index, 
							  username=config.db_user, password=config.db_pass)
		self.scan_interval = scan_interval_seconds
		self.idle_timeout = idle_timeout_seconds
		self.stop_event = threading.Event()
		self.config = config
		self._threads = []

		# database connection test
		self.db.ping()


	def start(self) -> None:
		""" Start the IDLE cleanup worker & expire cleanup worker in the background. """
		idle_cleanup_thread = threading.Thread(target=self._idle_cleanup_worker,
											   args=(self.scan_interval, self.idle_timeout),
											   name="IdleCleanupWorker",
											   daemon=True)

		expire_cleanup_thread = threading.Thread(target=self._expire_cleanup_worker,
												 name="ExpireCleanupWorker",
												 daemon=True)

		# log the threads
		self._threads.extend([idle_cleanup_thread, expire_cleanup_thread])


	def stop(self) -> bool:
		""" Stop all the created thread worker gracefully. """
		self.stop_event.set()
		for worker in self._threads:
			worker.join()

		return True


	def _idle_cleanup_worker(self, scan_interval_seconds: int, idle_timeout_seconds: int) -> None:
		""" Scan through the database a few minutes to terminate unactive session token. """
		pass


	def _expire_cleanup_worker(self) -> None:
		""" Event callback triggered when a key expired in database. """
		pass



if __name__ == "__main__":
	config = ValkeyConfig("localhost", 6379)
	manager = SessionManager(config)

	# register 5 tokens in batch
	for _ in range(0, 5):
		# manager.assign_token("chen5292", "127.0.0.1")
		pass

	# dump the active sessions
	active_sessions = manager.fetch_active_tokens("chen5292")
	print(active_sessions)