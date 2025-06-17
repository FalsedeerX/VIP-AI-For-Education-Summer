from fastapi import FastAPI
from sessionmanager.session import ValkeyConfig, SessionManager
from services.user_services import UserRouter
from services.chat_services import ChatRouter
from services.folder_services import router as folder_router


# pass in configuration
app = FastAPI()
valkey_config = ValkeyConfig("localhost", 6379)
manager = SessionManager(valkey_config)
user_router = UserRouter(manager)
chat_router = ChatRouter(manager)

# enable the routers
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(folder_router)
