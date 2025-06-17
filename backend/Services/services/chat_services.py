from fastapi import APIRouter, HTTPException, Depends
from databaseagent.database_async import DatabaseAgent
from .schemas.chat import NewChat, ChatMessage

router = APIRouter(prefix="/chats", tags=["chats"])
agent = DatabaseAgent()


@router.post("/create", response_model=int, status_code=201)
async def create_chat(payload: NewChat) -> int:
    """Create a new chat message."""
    try:
        print("I got here")
        id = await agent.create_chat(payload.user_id, payload.title)
    except Exception as e:
        raise HTTPException(404, "Could not create chat")
    return id


@router.get("/chat/{chat_id}", response_model=ChatMessage)
async def get_chat_message(chat_id: int):
    try:
        chat_history = await agent.get_chat_history(chat_id)
    except Exception as e:
        raise HTTPException(404, "Chat not found")
    return chat_history


@router.put("/chat/{chat_id}", status_code=204)
async def log_chat_message(chat_id: int, payload: NewChat):
    ok = False
    try:
        ok = await agent.log_chat(chat_id, payload.user_id, payload.message)
    except Exception as e:
        raise HTTPException(404, "Could not add message to chat")
    if not ok:
        raise HTTPException(404, "Cannot add message to chat")
    return


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(chat_id: int):
    ok = False
    try:
        ok = await agent.delete_chat(chat_id)
    except Exception as e:
        raise HTTPException(404, "Chat not found")
    if not ok:
        raise HTTPException(404, "Cannot delete chat")
    return

