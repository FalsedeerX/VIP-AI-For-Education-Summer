from fastapi import FastAPI
from services.user_services import router as user_router
from services.folder_services import router as folder_router
from services.chat_services import router as chat_router

app = FastAPI()

# mount each router on the single app
app.include_router(user_router)
app.include_router(folder_router)
app.include_router(chat_router)