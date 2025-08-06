import uvicorn
from uuid import UUID
from fastapi import FastAPI, Request
from services.user_services import UserRouter
from services.chat_services import ChatRouter
from services.folder_services import FolderRouter
from services.course_services import CourseRouter
from databaseagent.database_async import DatabaseAgent
from sessionmanager.session import ValkeyConfig, SessionManager
from fastapi.middleware.cors import CORSMiddleware
import os
import redis
from urllib.parse import urlparse

# pass in configuration
app = FastAPI()

PUBLIC_IP = os.getenv("NEXT_PUBLIC_IP", "localhost")
CHATBOT_WS_URL = f"ws://{PUBLIC_IP}:6666/ws"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  # default fallback for local dev

parsed_url = urlparse(REDIS_URL)
valkey_config = ValkeyConfig(
    db_host=parsed_url.hostname,
    db_port=parsed_url.port,
    db_user=parsed_url.username,
    db_pass=parsed_url.password
)
session_manager = SessionManager(valkey_config)
database_broker = DatabaseAgent()

# initialize the router
user_router = UserRouter(database_broker, session_manager)
chat_router = ChatRouter(database_broker, session_manager, CHATBOT_WS_URL)
folder_router = FolderRouter(database_broker, session_manager)
course_router = CourseRouter(database_broker, session_manager)


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
		request.state.is_admin = await database_broker.is_admin(request.state.user_id)

	response = await call_next(request)
	return response


# enable routers
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(folder_router.router)
app.include_router(course_router.router)


app.add_middleware(
  CORSMiddleware,
  allow_origins=[f"http://{PUBLIC_IP}:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

if __name__ == "__main__":
	uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)