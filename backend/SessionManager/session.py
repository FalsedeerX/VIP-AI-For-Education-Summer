import time
from types import TracebackType
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

		# insert session entry, reverse lookup and token tracking
		token = uuid4()
		self.db.setex(f"ip_address:{token}", ttl_seconds, ip_address)
		self.db.setex(f"session_user:{token}", ttl_seconds, username)
		self.db.zadd(f"user_sessions:{username}", {str(token): time.time()})
		return token


	def verify_token(self, username: str, ip_address: str, token: UUID) -> bool:
		""" Verify whether a certain token expired. """
		# validate IP format
		try:
			parsed_ip = ipaddress.ip_address(ip_address)
		except ValueError:
			return False

		# verify username and IP
		address_key = f"ip_address:{token}"
		username_key = f"session_user:{token}"
		if not self.db.exists(address_key) or not self.db.exists(username_key): return False
		if self.db.get(address_key) != ip_address or self.db.get(username_key) != username: return False

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
		if not entries: return None
		if not isinstance(entries, Sequence): return None
		if not isinstance(entries[0], str): return None
		return list(entries)


	def purge_all_tokens(self, username: str) -> int:
		""" Remove all tokens which belong to a specific user. Return number of session terminated. """
		purge_count = 0
		active_tokens = self.fetch_active_tokens(username)
		if active_tokens is None: return 0
		for token in active_tokens:
			if self.purge_token(UUID(token)):
				purge_count += 1

		return purge_count



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


	def start(self) -> bool:
		""" Start the IDLE cleanup worker & expire cleanup worker in the background. """
		try:
			idle_cleanup_thread = threading.Thread(target=self._idle_cleanup_worker, args=(self.scan_interval, self.idle_timeout), name="IdleCleanupWorker", daemon=True)
			expire_cleanup_thread = threading.Thread(target=self._expire_cleanup_worker, name="ExpireCleanupWorker", daemon=True)
			self._threads.extend([idle_cleanup_thread, expire_cleanup_thread])
		except Exception:
			return False
		return True


	def stop(self) -> bool:
		""" Stop all the created thread worker gracefully. """
		self.stop_event.set()
		for worker in self._threads:
			worker.join()

		return True


	def _idle_cleanup_worker(self, scan_interval_seconds: int, idle_timeout_seconds: int) -> None:
		""" Scan through the database a few minutes to terminate unactive session token. """
		while not self.stop_event.is_set():
			cutoff = time.time() - idle_timeout_seconds
			
			# walk through all the sessions owned by each user
			for user_sessions in self.db.scan_iter(match="user_sessions:*", count=100):
				idle_token = self.db.zrangebyscore(user_sessions, "-inf", cutoff)
				for token in idle_token:
					self.db.delete(f"session:{token}")
					self.db.zrem(user_sessions, token)

				# remove empty zlist if empty
				if self.db.zcard(user_sessions) == 0:
					self.db.delete(user_sessions)

			# wait for next scan or early exit
			self.stop_event.wait(scan_interval_seconds)


	def _expire_cleanup_worker(self) -> None:
		""" Event callback triggered when a key expired in database. """
		notification = self.db.pubsub()
		notification.psubscribe(f"__keyevent@{self.config.db_index}__:expired")

		# filter on the key expire event
		for message in notification.listen():
			if message.get('type') != "pmessage": continue
			expired_session = message.get('data')
			if not expired_session: continue

			# remove the key from tracking list
			_, _, token = expired_session.partition('session:')
			# if not self.db.zscore(f"user_sessions:{token}")



if __name__ == "__main__":
	config = ValkeyConfig("localhost", 6379)
	manager = SessionManager(config)

	# register 5 session tokens for chen5292
	token_list1 = []
	for _ in range(0, 5):
		token = manager.assign_token("chen5292", "127.0.0.1")
		token_list1.append(token)

	# register 3 session tokens for falsedeer
	token_list2 = []
	for _ in range(0, 5):
		token = manager.assign_token("falsedeer", "192.168.1.1")
		token_list2.append(token)

	# verify all the token owned by chen5292 registered at 127.0.0.1
	for token in token_list1:
		status = manager.verify_token("chen5292", "8.8.8.8", token)
		print(f"Verification status for chen5292: {status}")

	# verify all the token owned by falsedeer registered at 192.168.1.1
	for token in token_list2:
		status = manager.verify_token("falsedeer", "192.168.1.12", token)
		print(f"Verification status for falsedeer: {status}")