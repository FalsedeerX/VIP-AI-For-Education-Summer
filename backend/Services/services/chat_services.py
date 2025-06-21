from uuid import UUID
from sessionmanager.session import SessionManager
from databaseagent.database_async import DatabaseAgent
from services.schemas.chat import NewChat, ChatMessages, NewChatMessage
from fastapi import APIRouter, HTTPException, Request, Response


class ChatRouter:
	def __init__(self, database: DatabaseAgent, session: SessionManager):
		self.router = APIRouter(prefix="/chats", tags=["chats"])
		self.session = session
		self.db = database

		# register the endpoints
		self.router.post("/create", status_code=201, response_model=str)(self.create_chat)
		self.router.get("/{chat_id}", status_code=200, response_model=ChatMessages)(self.get_chat_message)
		self.router.put("/{chat_id}", status_code=200, response_model=bool)(self.log_chat_message)
		self.router.delete("/{chat_id}", status_code=200, response_model=bool)(self.delete_chat)


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
		""" Receive the chat log message in a dictionary """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		chat_history = await self.db.get_chat_history(chat_id)
		if not chat_history: raise HTTPException(404, "Invalid chatID or empty chat history.")
		return chat_history


	async def log_chat_message(self, chat_id: str, payload: NewChatMessage, request: Request, response: Response) -> bool:
		""" Log a new message entry into a speciifed chat by UUID. """
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		status = await self.db.log_chat(chat_id, request.state.user_id, payload.message)
		if not status: raise HTTPException(404, "Cannot add message to chat")
		return True


	async def delete_chat(self, chat_id: str, request: Request, response: Response) -> bool:
		""" 
		Delete a chat by a specific chat UUID.
		Avoid using this endpoint, the authentication method isn't well implemented.
		Currently all user which is logged in can delete arbitrary chat as long as their seesion token is valid. 
		"""
		# check if the user is logged in 
		if not request.state.token: raise HTTPException(401, "User not logged in.")

		# verify the session token
		if not self.session.verify_token(request.state.user_id, request.state.ip_address, UUID(request.state.token)):
			response.delete_cookie("purduegpt-token")
			raise HTTPException(401, "Malformed session token.")

		status = await self.db.delete_chat(chat_id)
		if not status: raise HTTPException(400, "Unable to delete chat.")
		return True


