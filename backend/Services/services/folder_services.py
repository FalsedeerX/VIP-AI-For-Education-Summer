from fastapi import APIRouter, HTTPException, Depends
from databaseagent.database_async import DatabaseAgent
from .schemas.folder import FolderCreate, FolderUpdate, FoldersWithChats

router = APIRouter(prefix="/folders", tags=["folders"])
agent = DatabaseAgent()


@router.post("/create", response_model=int, status_code=201)
async def create_folder(payload: FolderCreate) -> int:
    """Create a new folder for a user."""
    try:
        folder = await agent.create_folder(payload.name, payload.owner_id)
    except Exception as e:
        raise HTTPException(404, "Could not create folder")
    return folder


@router.get("/{owner_id}", response_model=FoldersWithChats)
async def get_folders(owner_id: int):
    folders = await agent.get_folders(owner_id)
    if folders is None:
        raise HTTPException(404, "No folders found for this user")
    return folders


@router.put("/organize/{folder_id}", status_code=204)
async def update_folder(folder_id: int, payload: FolderUpdate):
    ok = await agent.organize_chat(payload.chat_id, payload.folder_name)
    if not ok:
        raise HTTPException(404, "Cannot add chat to folder")
    return


@router.delete("/{folder_id}", status_code=204)
async def delete_folder(folder_id: int, owner_id: int):
    ok = await agent.delete_folder(owner_id, folder_id)
    if not ok:
        raise HTTPException(404, "Folder not found")
    return
