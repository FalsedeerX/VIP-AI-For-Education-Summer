from fastapi import APIRouter, HTTPException, Depends
from databaseagent.database_async import DatabaseAgent
from .schemas.user import UserCreate, UserLogin

router = APIRouter(prefix="/users", tags=["users"])
agent = DatabaseAgent()


@router.post("/register", status_code=201)
async def create_user(payload: UserCreate):
    """Create a new folder for a user."""
    try:
        user_id = await agent.register_user(payload.username, payload.email, payload.password)
    except Exception as e:
        raise HTTPException(404, "Could not register user")
    return user_id


@router.get("/id/{username}", response_model=int)
async def get_user_id(username: str):
    user_id = await agent.get_user_id(username)
    if user_id is None:
        raise HTTPException(404, "User not found")
    return user_id


@router.get("/auth/{user_id}", response_model=bool)
async def verify_user(payload: UserLogin):
    is_verified = await agent.verify_user(payload.user_id, payload.password)
    return is_verified


@router.delete("/{user_id}", status_code=204)
async def delete_user(payload: UserLogin):
    ok = await agent.delete_user(payload.username)
    if not ok:
        raise HTTPException(404, "User not found")
    return
