from uuid import UUID
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from services.schemas.folder import FolderCreate, FolderUpdate, FoldersWithChats
from fastapi import APIRouter, HTTPException, Request, Response


class FolderRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/folders", tags=["folders"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.get("/", response_model=FoldersWithChats)(self.get_folders)
		self.router.post("/create", response_model=int, status_code=201)(self.create_folder)
		self.router.put("/organize/{folder_id}", status_code=204)(self.organize_folder)
		self.router.delete("/{folder_id}", status_code=204)(self.delete_folder)


	async def get_folders(self, request: Request, response: Response) -> FoldersWithChats:
		""" Get a list of fodlers which the current user owns. """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		folders = await self.db.get_folders(request.state.user_id)
		if folders is None: raise HTTPException(404, "No folders found for this user")
		return folders


	async def create_folder(self, payload: FolderCreate) -> int:
		try:
			folder = await self.db.create_folder(payload.name, payload.owner_id)
		except Exception as e:
			raise HTTPException(404, "Could not create folder")
		return folder


	async def organize_folder(self, folder_id: int, payload: FolderUpdate):
		ok = await self.db.organize_chat(payload.chat_id, payload.folder_name)
		if not ok:
			raise HTTPException(404, "Cannot add chat to folder")
		return


	async def delete_folder(self, folder_id: int, owner_id: int):
		ok = await self.db.delete_folder(owner_id, folder_id)
		if not ok:
			raise HTTPException(404, "Folder not found")
		return

