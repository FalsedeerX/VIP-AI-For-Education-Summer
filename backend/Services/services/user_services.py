from databaseagent.database_async import DatabaseAgent
from sessionmanager.session import SessionManager
from services.schemas.user import UserCreate, UserLogin
from fastapi import APIRouter, HTTPException, Request, Response


class UserRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/users", tags=["users"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.post("/register", status_code=201)(self.create_user)
		self.router.post("/auth/{user_id}", response_model=bool)(self.login_user)
		self.router.get("/id/{username}", response_model=int)(self.get_user_id)
		self.router.delete("/{user_id}", status_code=204)(self.delete_user)


	async def create_user(self, payload: UserCreate) -> bool:
		""" Register a new user. """
		status = await self.db.register_user(payload.username, payload.email, payload.password)
		if not status:
			raise HTTPException(status_code=409, detail="Registration info conflict.")
		return True


	async def login_user(self, payload: UserLogin, request: Request, response: Response) -> bool:
		""" Verify a user credential, if approved, will assign a token in cookie """
		status = await self.db.verify_user(payload.user_id, payload.password)
		if not status: raise HTTPException(status_code=403, detail="User authentication failed.")

		# resolve the clients IP		
		return True


	async def get_user_id(self, username: str) -> int:
		""" Resolve the current user's username into ID. User are only allowed to query their own ID. """
		user_id = await self.db.get_user_id(username)
		if user_id is None:
			raise HTTPException(404, "User not found")
		return user_id


	async def delete_user(self, payload: UserLogin):
		ok = await self.db.delete_user(payload.username)
		if not ok:
			raise HTTPException(404, "User not found")
		return

