from uuid import UUID
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from fastapi import APIRouter, HTTPException, Request, Response
from services.schemas.course import CourseContent, CourseInfo, NewCourse


class CourseRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/courses", tags=["courses"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.get("", status_code=200, response_model=CourseContent)(self.get_courses)
		self.router.post("/create", status_code=200, response_model=int)(self.create_course)
		self.router.delete("/delete", status_code=200, response_model=bool)(self.delete_course)


	async def get_courses(self, request: Request, response: Response) -> CourseContent:
		""" Get a list of courses and the folders which the user own. 
			Return in dictionary 'course-title: list[folder_id]' """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		# query the chat, folder relationship of the current user
		status = await self.db.get_courses(request.state.user_id)
		return status


	async def create_course(self, payload: NewCourse, request: Request, response: Response) -> int:
		""" Create a new course entry. On success return course ID. On failure returns -1 """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		course_id = await self.db.create_course(payload.course_code, payload.course_title)
		return course_id


	async def delete_course(self, payload: CourseInfo, request: Request, response: Response) -> bool:
		""" Delete the coruse and every related folders and chat, which is referencing it. """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		status = await self.db.delete_course(payload.course_id)
		return status


if __name__ == "__main__":
	pass


