import re
import uvicorn
from uuid import UUID
from fastapi import FastAPI, Request
from services.user_services import UserRouter
from services.chat_services import ChatRouter
from services.folder_services import FolderRouter
from databaseagent.database_async import DatabaseAgent
from sessionmanager.session import ValkeyConfig, SessionManager

# pass in configuration
app = FastAPI()
valkey_config = ValkeyConfig("localhost", 6379)
session_manager = SessionManager(valkey_config)
database_broker = DatabaseAgent()

# initialize the router
user_router = UserRouter(database_broker, session_manager)
chat_router = ChatRouter(database_broker, session_manager)
folder_router = FolderRouter(database_broker, session_manager)


@app.middleware("http")
async def auto_resolve(request: Request, call_next):
	""" A middleware to make your life eaiser. """
	token = request.cookies.get("purduegpt-token")
	request.state.ip_address = request.client.host
	request.state.user_id = -1
	request.state.token = None

	# parse the token owner automatically if present
	if token:
		request.state.token = token
		request.state.user_id = session_manager.query_owner(UUID(token))

	response = await call_next(request)
	return response


# enable routers
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(folder_router.router)


if __name__ == "__main__":
	uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)