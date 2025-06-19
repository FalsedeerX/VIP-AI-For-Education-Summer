from fastapi import APIRouter, HTTPException, Depends
from databaseagent.database_async import DatabaseAgent
from services.schemas.folder import FolderCreate, FolderUpdate, FoldersWithChats
from sessionmanager.session import SessionManager
#from .schemas.folder import FolderCreate, FolderUpdate, FoldersWithChats


class FolderRouter:
	def __init__(self, session: SessionManager):
		self.router = APIRouter(prefix="/folders", tags=["folders"])
		self.db = DatabaseAgent()
		self.manager = session

		# register the endpoints
		self.router.post("/create", response_model=int, status_code=201)(self.create_folder)
		self.router.get("/{owner_id}", response_model=FoldersWithChats)(self.get_folders)
		self.router.put("/organize/{folder_id}", status_code=204)(self.update_folder)
		self.router.delete("/{folder_id}", status_code=204)(self.delete_folder)


	async def get_folders(self, owner_id: int):
		folders = await self.db.get_folders(owner_id)
		if folders is None:
			raise HTTPException(404, "No folders found for this user")
		return folders


	async def create_folder(self, payload: FolderCreate) -> int:
		try:
			folder = await self.db.create_folder(payload.name, payload.owner_id)
		except Exception as e:
			raise HTTPException(404, "Could not create folder")
		return folder


	async def update_folder(self, folder_id: int, payload: FolderUpdate):
		ok = await self.db.organize_chat(payload.chat_id, payload.folder_name)
		if not ok:
			raise HTTPException(404, "Cannot add chat to folder")
		return


	async def delete_folder(self, folder_id: int, owner_id: int):
		ok = await self.db.delete_folder(owner_id, folder_id)
		if not ok:
			raise HTTPException(404, "Folder not found")
		return

