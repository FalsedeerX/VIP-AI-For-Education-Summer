from fastapi import APIRouter, HTTPException, Depends
from databaseagent.database_async import DatabaseAgent
from services.schemas.chat import NewChat, ChatMessage
from sessionmanager.session import SessionManager
from .schemas.chat import NewChat, ChatMessage


class ChatRouter:
	def __init__(self, session: SessionManager):
		self.router = APIRouter(prefix="/chats", tags=["chats"])
		self.db = DatabaseAgent()
		self.manager = session

		# register the endpoints
		self.router.post("/create", response_model=int, status_code=201)(self.create_chat)
		self.router.get("/{chat_id}", response_model=ChatMessage)(self.get_chat_message)
		self.router.put("/{chat_id}", status_code=204)(self.log_chat_message)
		self.router.delete("/{chat_id}", status_code=204)(self.delete_chat)


	async def create_chat(self, payload: NewChat) -> int:
		try:
			id = await self.db.create_chat(payload.user_id, payload.title)
		except Exception as e:
			raise HTTPException(404, "Could not create chat")
		return id


	async def get_chat_message(self, chat_id: int):
		try:
			chat_history = await self.db.get_chat_history(chat_id)
		except Exception as e:
			raise HTTPException(404, "Chat not found")
		return chat_history


	async def log_chat_message(self, chat_id: int, payload: NewChat):
		ok = False
		try:
			ok = await self.db.log_chat(chat_id, payload.user_id, payload.message)
		except Exception as e:
			raise HTTPException(404, "Could not add message to chat")
		if not ok:
			raise HTTPException(404, "Cannot add message to chat")
		return


	async def delete_chat(self, chat_id: int):
		ok = False
		try:
			ok = await seld.db.delete_chat(chat_id)
		except Exception as e:
			raise HTTPException(404, "Chat not found")
		if not ok:
			raise HTTPException(404, "Cannot delete chat")
		return


