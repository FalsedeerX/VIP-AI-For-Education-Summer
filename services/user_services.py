# main.py
from fastapi import FastAPI, HTTPException
from backend.DatabaseAgent.database_v2 import DatabaseAgent
from schemas.user import UserCreate, UserLogin
app = FastAPI()
agent = DatabaseAgent()

@app.post(
    "/users/",
    status_code=201,
)
async def api_create_user(payload: UserCreate):
    """Create a new folder for a user."""
    try:
        user_id = await agent.create_folder(payload.username, payload.email, payload.password)
    except Exception as e:
        raise HTTPException(404, "Could not register user")
    return user_id

@app.get("/users/{username}", response_model=int)
async def api_get_user_id(username: str):
    user_id = await agent.get_user_id(username)
    if user_id is None:
        raise HTTPException(404, "User not found")
    return 

@app.get("/users/{user_id}", response_model=bool)
async def api_verify_user(payload: UserLogin):
    is_verified = await agent.verify_user(payload.user_id, payload.password)
    return is_verified

@app.delete("/users/{user_id}", status_code=204)
async def api_delete_folder(payload: UserLogin):
    ok = await agent.delete_user(payload.username)
    if not ok:
        raise HTTPException(404, "User not found")
    return
