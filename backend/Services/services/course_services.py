from uuid import UUID
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from fastapi import APIRouter, HTTPException, Request, Response


class CourseRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/courses", tags=["courses"])
		self.session = session
		self.db = database

		# register the endpoints


	async def get_courses(self):
		""" Get a list of courses and the folders which the user own. """
		pass


	async def delete_course(self):
		""" Delete the coruse any every chat, course which is referencing it. """
		pass


if __name__ == "__main__":
	pass


