import json
import websockets
from uuid import UUID
from http.cookies import SimpleCookie
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from fastapi import APIRouter, WebSocket, HTTPException, Request, Response, WebSocketDisconnect
from services.schemas.chat import NewChat, ChatMessages, ChatOrganize, ChatOwner

class ChatRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager, chatbot_url: str):
		self.chatbot_url = chatbot_url
		self.router = APIRouter(prefix="/chats", tags=["chats"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.post("/create", status_code=201, response_model=str)(self.create_chat)
		self.router.get("/random", status_code=200, response_model=str)(self.get_random_chat)
		self.router.post("/organize", status_code=200, response_model=bool)(self.organize_chat)
		self.router.get("/{chat_id}", status_code=200, response_model=ChatMessages)(self.get_chat_message)
		self.router.delete("/delete/{chat_id}", status_code=200, response_model=bool)(self.delete_chat)
		self.router.add_api_websocket_route("/relay/{chat_id}", self.websocket_relay)
		self.router.get("/owner/{chat_id}", status_code=200, response_model=ChatOwner)(self.get_chat_owner)


	async def create_chat(self, payload: NewChat, request: Request, response: Response) -> str:
		""" Create a new chat of a specified title for the current logged in user. """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		id = await self.db.create_chat(request.state.user_id, payload.title)
		return id


	async def get_random_chat(self, request: Request, response: Response) -> str|None:
		""" Retrieve random chat from the current user. """
		# check if the user is logged in
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		# retrieve a random chat-id
		chat_id = await self.db.get_random_chat(request.state.user_id)
		return chat_id


	async def get_chat_message(self, chat_id: str, request: Request, response: Response) -> ChatMessages:
		""" Receive the chat messages in a dictionary """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		chat_history = await self.db.get_chat_history(chat_id)
		if chat_history is None: raise HTTPException(404, "Invalid id or chat does not exist.")
		return chat_history


	async def get_chat_owner(self, chat_id: str, request: Request, response: Response) -> ChatOwner:
		""" Receive the chat owner in a dictionary """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		chat_owner = await self.db.get_chat_owner(chat_id)
		if chat_owner is None: raise HTTPException(404, "Invalid id or chat does not exist.")
		return {"owner_id": chat_owner}


	async def websocket_relay(self, websocket: WebSocket, chat_id: str):
		""" Establish a connection from client to transmit data,
			WARNING: authentication is disabled on this endpoint due to cross origin cookie problem. """
		# establish websocket connection
		await websocket.accept()

		try:
			while True:
				# send the question to chatbot
				question = await websocket.receive_text()
				async with websockets.connect(self.chatbot_url) as upstream:
					request = {
						"action": "generate_answer",
						"data": {
						"question": question
					}
				}
				await upstream.send(json.dumps(request))

				# receive response from chatbot
				async for message in upstream:
					try:
						msg = json.loads(message)
						mtype = msg.get("type")
						if mtype == "stream_chunk":
							await websocket.send_text(msg.get("content", ""))
						else:
							break
					except:
						break

		except:
			await websocket.close()


	async def delete_chat(self, chat_id: str, request: Request, response: Response) -> bool:
		""" Delete a chat by a specific chat UUID. """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		# verify chat ownership
		chat_owner_id = await self.db.get_chat_owner(chat_id)
		if request.state.user_id != chat_owner_id: raise HTTPException(401, "Access denied.")

		status = await self.db.delete_chat(chat_id)
		if not status: raise HTTPException(400, "Unable to delete chat.")
		return True


	async def organize_chat(self, payload: ChatOrganize, request: Request, response: Response) -> bool:
		""" Organize a chat into a folder. """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		# receive the actual owner of the chat and folder 
		chat_owner_id = await self.db.get_chat_owner(payload.chat_id)		
		folder_owner_id = await self.db.get_folder_owner(payload.folder_id)
		if chat_owner_id == -1 or folder_owner_id == -1: raise HTTPException(404, "Target chat or folder doens't exist")

		# verify if current user is the owner
		if request.state.user_id != chat_owner_id: raise HTTPException(401, "Access denied.")
		status = await self.db.organize_chat(payload.chat_id, payload.folder_id)
		if not status: raise HTTPException(404, "Failed assigning chat to folder.")
		return True
