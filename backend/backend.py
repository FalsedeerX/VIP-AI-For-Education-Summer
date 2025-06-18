import uvicorn
from fastapi import FastAPI
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

# enable routers
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(folder_router.router)


if __name__ == "__main__":
	uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)