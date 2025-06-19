from fastapi import APIRouter, HTTPException, Depends
from databaseagent.database_async import DatabaseAgent
from sessionmanager.session import SessionManager
from services.schemas.user import UserCreate, UserLogin


class UserRouter:
	def __init__(self, session: SessionManager):
		self.router = APIRouter(prefix="/users", tags=["users"])
		self.db = DatabaseAgent()
		self.manager = session

		# register the endpoints
		self.router.post("/register", status_code=201)(self.create_user)
		self.router.get("/id/{username}", response_model=int)(self.get_user_id)
		self.router.post("/auth/{user_id}", response_model=bool)(self.verify_user)
		self.router.delete("/{user_id}", status_code=204)(self.delete_user)


	async def create_user(self, payload: UserCreate):
		try:
			user_id = await self.db.register_user(payload.username, payload.email, payload.password)
		except Exception as e:
			raise HTTPException(404, "Could not register user")
		return user_id


	async def get_user_id(self, username: str):
		user_id = await self.db.get_user_id(username)
		if user_id is None:
			raise HTTPException(404, "User not found")
		return user_id


	async def verify_user(self, payload: UserLogin):
		is_verified = await self.db.verify_user(payload.username, payload.password)
		return is_verified


	async def delete_user(self, payload: UserLogin):
		ok = await self.db.delete_user(payload.username)
		if not ok:
			raise HTTPException(404, "User not found")
		return

