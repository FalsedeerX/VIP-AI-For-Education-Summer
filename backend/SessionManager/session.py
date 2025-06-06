import time
import redis
import threading
from uuid import UUID, uuid4
from ipaddress import _BaseAddress
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
							  username=config.db_user, password=config.db_pass)
		self.db.ping()


	def assign_token(self, username: str, time_to_live: int) -> UUID:
		""" Assigning authenciated user with an UUID as the session token. """
		token = uuid4()
		key_name = f"session:{token}"

		return token


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

