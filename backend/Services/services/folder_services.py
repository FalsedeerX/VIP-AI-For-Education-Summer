import json
from uuid import UUID
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from fastapi import APIRouter, HTTPException, Request, Response, Form, File, UploadFile, websockets
from services.schemas.folder import NewFolder, FolderOrganize, FolderInfo, ChatOut
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import base64
from http.cookies import SimpleCookie


class FolderRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager, chatbot_url: str):
		self.router = APIRouter(prefix="/folders", tags=["folders"])
		self.session = session
		self.db = database
		self.chatbot_url = chatbot_url

		# register the endpoints
		self.router.post("", status_code=200, response_model=List[ChatOut])(self.get_folder)
		self.router.post("/create", status_code=201, response_model=int)(self.create_folder)
		self.router.delete("/delete", status_code=200, response_model=bool)(self.delete_folder)
		self.router.post("/organize", status_code=200, response_model=bool)(self.organize_folder)
		self.router.add_api_websocket_route("/upload", self.websocket_file_upload)


	async def get_folder(self, payload: FolderInfo, request: Request, response: Response) -> List[ChatOut]:
		""" Get a list of chats which is organized in a specific folder_id """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")
		
		rows = await self.db.get_chats(payload.folder_id, request.state.user_id)
		return [ChatOut(chat_id=r["id"], title=r["title"]) for r in rows]


	async def create_folder(self, payload: NewFolder, request: Request, response: Response) -> int:
		""" Create a new folder under a folder. """
		# check if the user is logged in
		if not request.state.is_admin: return -1

		folder_id = await self.db.create_folder(payload.folder_name, payload.course_id, request.state.user_id)
		if folder_id == -1: raise HTTPException(404, "Could not create folder")
		return folder_id


	async def delete_folder(self, payload: FolderInfo, request: Request, response: Response) -> bool:
		""" Remove a folder permanently. """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		status = await self.db.delete_folder(payload.folder_id)
		if not status: raise HTTPException(404, "Target folder couldn't be found.")
		return True


	async def organize_folder(self, payload: FolderOrganize, request: Request, response: Response) -> bool:
		""" Organize a folder into a course """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		status = await self.db.organize_folder(payload.folder_id, payload.course_id)
		if not status: raise HTTPException(404, "Target folder couldn't be found.")
		return True
	

	async def upload_file(self, request: Request, response: Response, file: UploadFile = File(...), folder_id: int = Form(...), file_name: str = Form(...),) -> dict:
		user_id = request.state.user_id

		if not request.state.token:
			raise HTTPException(status_code=401, detail="User not logged in.")
		
		if not request.app.state.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(status_code=401, detail="Malformed session token.")

		try:
			pdf_bytes = await file.read()
			if not pdf_bytes:
				raise HTTPException(status_code=400, detail="Empty file uploaded.")
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"Failed to parse PDF")

		encoded_base64_bytes = base64.b64encode(pdf_bytes)
		pdf_text = encoded_base64_bytes.decode('utf-8')

		try:
			async with websockets.connect(self.chatbot_url) as upstream:
				await upstream.send(json.dumps({
					"action": "upload_context",
					"data": {
						"folder": f"folder_{folder_id}",
						"file_name": file_name,
						"text": pdf_text,
						"user_id": user_id
					}
				}))
				# No response expected
		except Exception as e:
			raise HTTPException(500, f"Failed to send context to chatbot")

		return {"message": "File uploaded and sent to chatbot as context."}