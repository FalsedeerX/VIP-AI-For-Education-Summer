import time
import redis
import threading
import ipaddress
from typing import Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from collections.abc import Sequence, Iterable


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
							  username=config.db_user, password=config.db_pass, decode_responses=True, ssl=True)
		self.config = config
		self.db.ping()


	def assign_token(self, user_id: int, ip_address: str, ttl_seconds: int = 10800) -> UUID|None:
		""" Assigning authenciated user with an UUID as the session token. """
		# validate IP format
		try:
			parsed_ip = ipaddress.ip_address(ip_address)
		except ValueError:
			return None

		# insert session entry, reverse lookup and token tracking
		token = uuid4()
		self.db.set(f"user_id:{token}", user_id)
		self.db.setex(f"ip_address:{token}", ttl_seconds, ip_address)
		self.db.zadd(f"user_sessions:{user_id}", {str(token): time.time()})
		return token


	def verify_token(self, user_id: int, ip_address: str, token: UUID) -> bool:
		""" Verify whether a certain token expired. """
		# validate IP format
		try:
			parsed_ip = ipaddress.ip_address(ip_address)
		except ValueError:
			return False

		# verify username and IP
		id_key = f"user_id:{token}"
		address_key = f"ip_address:{token}"
		if not self.db.exists(address_key) or not self.db.exists(id_key): return False
		if self.db.get(address_key) != ip_address or int(self.db.get(id_key)) != user_id: return False

		# update the score in session tracking
		self.db.zadd(f"user_sessions:{user_id}", {str(token): time.time()})
		return True


	def extend_token(self, token: UUID, extend_seconds: int) -> bool:
		""" Extend the user session for a specific amount of time. """
		# check if the key expired already (-2) or not expirable (-1)
		# and we will leave a 10 second internal delay to avoid race condition
		address_key = f"ip_address:{token}"
		ttl = self.db.ttl(address_key)
		if not isinstance(ttl, int): return False
		if ttl <= 5: return False

		# update the remaining time-to-live
		if ttl + extend_seconds < 0: return False
		self.db.expire(address_key, ttl + extend_seconds)
		return True


	def purge_token(self, token: UUID) -> bool:
		""" Remove a specific token from a user. """
		# check whether the key exist in database & username
		id_key = f"user_id:{token}"
		address_key = f"ip_address:{token}"
		if not self.db.get(id_key) or not self.db.get(address_key): return False

		# remove key and untrack session
		self.db.zrem(f"user_sessions:{self.db.get(id_key)}", str(token))
		self.db.delete(address_key)
		self.db.delete(id_key)
		return True


	def query_owner(self, token: UUID) -> int:
		""" Query the owner of a certain token. Returns -1 if failed. """
		id_key = f"user_id:{token}"
		user_id = self.db.get(id_key)
		if not user_id: return -1
		return int(user_id)


	def fetch_active_tokens(self, user_id: int) -> list[str]|None:
		""" Fetch all active session tokens from a certain user """
		entries = self.db.zrange(f"user_sessions:{user_id}", 0, -1)
		if not entries: return None
		if not isinstance(entries, Sequence): return None
		if not isinstance(entries[0], str): return None
		return list(entries)


	def purge_all_tokens(self, user_id: int) -> int:
		""" Remove all tokens which belong to a specific user. Return number of session terminated. """
		purge_count = 0
		active_tokens = self.fetch_active_tokens(user_id)
		if active_tokens is None: return 0
		for token in active_tokens:
			if self.purge_token(UUID(token)):
				purge_count += 1

		return purge_count



class SessionWorker:
	def __init__(self, manager: SessionManager, scan_interval_seconds: int = 60, idle_timeout_seconds: int = 3600):
		self.manager = manager
		self.db = manager.db
		self.config = manager.config
		self.scan_interval = scan_interval_seconds
		self.idle_timeout = idle_timeout_seconds
		self.stop_event = threading.Event()
		self._threads = []
		self.db.ping()


	def start(self) -> bool:
		""" Start the IDLE cleanup worker & expire cleanup worker in the background. """
		try:
			idle_cleanup_thread = threading.Thread(target=self._idle_cleanup_worker, args=(self.scan_interval, self.idle_timeout), name="IdleCleanupWorker", daemon=True)
			expire_cleanup_thread = threading.Thread(target=self._expire_cleanup_worker, name="ExpireCleanupWorker", daemon=True)
			
			# start the thread workers and track them
			idle_cleanup_thread.start()
			expire_cleanup_thread.start()
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
			for user in self.db.scan_iter(match="user_sessions:*", count=100):
				idle_token = self.db.zrangebyscore(user, "-inf", cutoff)
				if not isinstance(idle_token, Iterable): continue
				for token in idle_token:
					self.manager.purge_token(token)

			# wait for next scan or early exit
			self.stop_event.wait(scan_interval_seconds)


	def _expire_cleanup_worker(self) -> None:
		""" Event callback triggered when a key expired in database. """
		notification = self.db.pubsub()
		notification.psubscribe(f"__keyevent@{self.config.db_index}__:expired")

		# filter on the key expire event `username:{token}`, ignore others
		while not self.stop_event.is_set():
			message = notification.get_message(timeout=1)
			if not message: continue
			if message.get('type') != "pmessage": continue
			expired_session = message.get('data')
			if not expired_session: continue
			if not expired_session.startswith("ip_address:"): continue

			# parse and search the corresponding username
			_, _, token = expired_session.partition("ip_address:")
			user_id = self.db.get(f"user_id:{token}")
			if not user_id: continue

			# untrack the session from ZLIST
			self.db.zrem(f"user_sessions:{user_id}", token)
			self.db.delete(f"user_id:{token}")



if __name__ == "__main__":
	# sample config, scan every 60 seonds and purging IDLE session which is unactive over 30 seconds
	config = ValkeyConfig("localhost", 6379)
	manager = SessionManager(config)
	worker = SessionWorker(manager, 10, 60)
	
	print("Starting the thread worker.")
	status = worker.start()
	print("status:", status)

	# dummy insert of session and make it IDLE for 30+ seconds
	token = manager.assign_token(23, "192.168.1.1")
	token = manager.assign_token(23, "192.168.1.2")
	user_id = manager.query_owner(token)
	print("User ID:", user_id)
	time.sleep(60)

	print("Stopping the thread worker.")
	status = worker.stop()
	print("status:", status)
