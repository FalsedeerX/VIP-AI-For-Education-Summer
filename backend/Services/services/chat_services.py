from uuid import UUID
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from fastapi import APIRouter, WebSocket, HTTPException, Request, Response, WebSocketDisconnect
from services.schemas.chat import NewChat, ChatMessages, NewChatMessage, ChatOrganize


class ChatRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/chats", tags=["chats"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.post("/create", status_code=201, response_model=str)(self.create_chat)
		self.router.post("/organize", status_code=200, response_model=bool)(self.organize_chat)
		self.router.get("/{chat_id}", status_code=200, response_model=ChatMessages)(self.get_chat_message)
		self.router.delete("/{chat_id}", status_code=200, response_model=bool)(self.delete_chat)
		self.router.add_api_websocket_route("/relay/{chat_id}", self.websocket_relay)


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


	async def get_chat_message(self, chat_id: str, request: Request, response: Response) -> ChatMessages:
		""" Receive the chat messages in a dictionary """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		chat_history = await self.db.get_chat_history(chat_id)
		if not chat_history: raise HTTPException(404, "Invalid chatID or empty chat history.")
		return chat_history


	# async def log_chat_message(self, chat_id: str, payload: NewChatMessage, request: Request, response: Response) -> bool:
	# 	""" Log a new message entry into a speciifed chat by UUID. """
	# 	# check if the user is logged in 
	# 	if not request.state.token: raise HTTPException(401, "User not logged in.")

	# 	# verify the session token
	# 	if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
	# 		response.delete_cookie("purduegpt-token")
	# 		raise HTTPException(401, "Malformed session token.")
		
	# 	# redirect the message to chatbot via websokcet
		
	# 	# fetch response from AI model
		
	# 	# log the user request into database
		
	# 	# log the model respone into database

	# 	status = await self.db.log_chat(chat_id, request.state.user_id, payload.message)
	# 	if not status: raise HTTPException(404, "Cannot add message to chat")
	# 	return True

	async def websocket_relay(self, websocket: WebSocket, chat_id: str):
		""" Establish a connection from client to transmit data """
		print(f"✅ WebSocket relay endpoint hit for chat_id: {chat_id}")
		raw_cookie = websocket.headers.get("cookie")
		await websocket.accept()

		try:
			while True:
				# receive the message from user
				question = await websocket.receive_text()

				# receive the response from AI
				answer = question
				await websocket.send_text(answer)

				# log user's message into database
				
				# log AI's response into database

		except WebSocketDisconnect:
			return



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
		if request.state.user_id != chat_owner_id or request.state.user_id != folder_owner_id: raise HTTPException(401, "Access denied.")
		status = await self.db.organize_chat(payload.chat_id, payload.folder_id)
		if not status: raise HTTPException(404, "Failed assigning chat to folder.")
		return True