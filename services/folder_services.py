# main.py
from fastapi import FastAPI, HTTPException, Depends
from backend.DatabaseAgent import create_folder, delete_folder, get_folder, organize_chat
from schemas.folder import FolderCreate, FolderOut, FolderUpdate, FoldersWithChats

app = FastAPI()

@app.post(
    "/folders/",
    response_model=FolderOut,
    status_code=201,
)
def api_create_folder(payload: FolderCreate):
    new = create_folder(payload.name, payload.owner_id)
    return new

@app.get("/folders/{folder_id}", response_model=FoldersWithChats)
def api_get_folder(folder_id: int):
    folder = get_folder(folder_id)
    if not folder:
        raise HTTPException(404, "Folder not found")
    return folder

@app.put("/folders/{folder_id}", status_code=204)
def api_update_folder(folder_id: int, payload: FolderUpdate):
    if not organize_chat(payload.chat_id, payload.folder_name):
        raise HTTPException(404, "Cannot add chat")
    return

@app.delete("/folders/{folder_id}", status_code=204)
def api_delete_folder(folder_id: int, owner_id: int):
    if not delete_folder(owner_id, folder_id):
        raise HTTPException(404, "Folder not found")
    return
