from uuid import UUID
from databaseagent.database_async import DatabaseAgent
from sessionmanager.session import SessionManager
from services.schemas.user import UserCreate, UserLogin, UserInfo, UserCourse, UserCourseList
from fastapi import APIRouter, HTTPException, Request, Response, requests


class UserRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/users", tags=["users"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.post("/auth", status_code=200, response_model=bool)(self.login_user)
		self.router.post("/register", status_code=201, response_model=bool)(self.create_user)
		self.router.delete("/delete", status_code=200, response_model=bool)(self.delete_user)
		self.router.get("/me", status_code=200, response_model=dict)(self.get_current_user)
		self.router.post("/logout", status_code=200, response_model=bool)(self.logout_user)
		self.router.post("/joincourse", status_code=200, response_model=bool)(self.join_course)
		self.router.post("/deletecourse", status_code=200, response_model=bool)(self.delete_course)
		self.router.get("/getcourses", status_code=200, response_model=UserCourseList)(self.get_user_course)


	async def create_user(self, payload: UserCreate) -> bool:
		""" Register a new user. """
		status = await self.db.register_user(payload.username, payload.email, payload.password, payload.is_admin)
		if not status: raise HTTPException(status_code=409, detail="Registration info conflict.")
		return True


	async def login_user(self, payload: UserLogin, request: Request, response: Response) -> bool:
		""" Verify user credential, if approved, will assign a token in cookie """
		status = await self.db.verify_user(payload.username, payload.password)
		if not status: raise HTTPException(status_code=403, detail="User authentication failed.")
		
		# authentication success, assign token and set cookie
		user_id = await self.db.get_user_id(payload.username)
		token = self.session.assign_token(user_id, request.state.ip_address)
		response.set_cookie(key="purduegpt-token", value=str(token), httponly=True, samesite="none", secure=True, max_age=10800, path="/") 
		return True


	async def delete_user(self, payload: UserInfo, request: Request, response: Response) -> bool:
		""" Meant for user deletion, but this thing needs a better design,
			currently this implemtation is flawed allowing all login user to delete other's account. """
		# if the user is not logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		# proceed the user deletion
		status = await self.db.delete_user(payload.user_id)
		if not status: raise HTTPException(404, "User not found")
		return True
	
	
	async def get_current_user(self, request: Request, response: Response) -> dict:
		"""
		Returns the currently authenticated user.
		Relies on your middleware having populated request.state.token and request.state.user_id.
		"""
		token = request.state.token
		user_id = request.state.user_id

		if not token:
			raise HTTPException(status_code=401, detail="Not authenticated.")

		try:
			ok = self.session.verify_token(
				user_id,
				request.state.ip_address,
				UUID(token)
			)
		except ValueError:
			ok = False

		if not ok:
			response.delete_cookie("purduegpt-token", path="/")
			raise HTTPException(status_code=401, detail="Session expired or invalid.")

		user = await self.db.get_username(user_id)
		if user is None:
			raise HTTPException(status_code=404, detail="User not found.")
		
		admin = await self.db.get_admin(user_id)

		return {"id": user_id, "username": user, "admin": admin}
	
	
	async def logout_user(self, request: Request, response: Response) -> bool:
		""" Logout the user by deleting the session token """
		token = request.state.token
		if not token:
			raise HTTPException(status_code=401, detail="Not authenticated.")

		try:
			ok = self.session.verify_token(
				request.state.user_id,
				request.state.ip_address,
				UUID(token)
			)
		except ValueError:
			ok = False

		if not ok:
			response.delete_cookie("purduegpt-token", path="/")
			raise HTTPException(status_code=401, detail="Session expired or invalid.")

		self.session.purge_token(UUID(token))
		response.delete_cookie("purduegpt-token", path="/")
		return True
	
	async def join_course(self, payload: UserCourse, request: Request) -> bool:
		""" Add a course to the user's course list """
		if not request.state.token:
			raise HTTPException(status_code=401, detail="User not logged in.")

		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			raise HTTPException(status_code=401, detail="Malformed session token.")

		uid = request.state.user_id
		ok = await self.db.add_course(uid, payload.course_code)
		if not ok:
			raise HTTPException(404, "Course not found or already added.")

		return True
	
	async def delete_course(self, payload: UserCourse, request: Request) -> bool:
		""" Delete a course from the user's course list """
		if not request.state.token:
			raise HTTPException(status_code=401, detail="User not logged in.")

		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			raise HTTPException(status_code=401, detail="Malformed session token.")

		uid = request.state.user_id
		ok = await self.db.delete_user_course(uid, payload.course_code)
		if not ok:
			raise HTTPException(404, "Course not found or already deleted.")

		return True
	
	async def get_user_course(self, request: Request) -> UserCourseList:
		""" Get the list of courses the user is enrolled in """
		if not request.state.token:
			raise HTTPException(status_code=401, detail="User not logged in.")

		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			raise HTTPException(status_code=401, detail="Malformed session token.")

		uid = request.state.user_id
		courses = await self.db.get_user_courses(uid)
		if courses is None:
			raise HTTPException(status_code=404, detail="No courses found for this user.")
		
		return courses
	
