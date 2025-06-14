# AI for Education Backend

This is the backend service for AI For Education, a chat-based application that helps users organize conversations by course and folder. It supports secure user authentication, asynchronous database operations, and modular service architecture.

## Project Structure

```txt
backend/
├── DatabaseAgent/
│   ├── database_async.py    # Async PostgreSQL connection & methods
│   ├── database_v2.py       # Alternate or refactored database logic
│   ├── reset.py             # Script to clear/truncate tables and to view current db
│   └── test_database_agent.py
├── services/
│   ├── chat_services.py     # Logic for chat handling
│   ├── folder_services.py   # Folder creation, update, linking
│   └── user_services.py     # User auth, registration, validation
├── schemas/
│   ├── chat.py
│   ├── folder.py
│   └── user.py
├── SessionManager/
│   └── session.py           # Session-based data management
├── Utils/
│   ├── mods/
│   │   ├── __init__.py
│   │   └── hd.py
│   └── echo_server.py
├── README.md                  # FastAPI app entry point
└── requirements.txt         # Python dependencies
```

## Core Features

Secure User Authentication using Argon2 hashing
Organized Conversations by folders and courses
Asynchronous interactions with PostgreSQL
Yestable Design with isolated services and schema layers
UID-based Chat Linking with folder associations
Database Schema

## Getting Started

1. Clone the Repository
   git clone
   cd backend
2. Install Dependencies
   pip install -r requirements.txt
3. Setup Environment
   Create a .env file in the root directory with:

   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=yourdbname
   DB_USER=yourdbuser
   DB_PASSWD=yourdbpass

4. Run the Server
   ???

## Database Schema Design

Refer to the SQL definitions in the /schemas section above for how to initialize your tables.
users — stores secure user accounts
courses — allows chats/folders to be organized by course
folders — user-defined containers for chat threads
chat_folder_link — many-to-many link between chats and folders
chats — contains metadata for each chat thread
chat_messages — logs every user/bot message
See the full schema here [Database Agent Docs](/backend/DatabaseAgent/README.md)

## Session Managment

This backend uses a custom session system powered by Redis to manage user logins.
Each authenticated user receives a unique UUID token tied to their IP address.
A background worker monitors session activity and:

- Expires tokens after inactivity or TTL timeout
- Allows session verification and extension via service methods

See the more on session managment [Session Manager Docs](/backend/SessionManager/README.md),
this system supports multi-session tracking, secure IP validation, and idle cleanup.

## Running Tests

pytest DatabaseAgent/test_database_agent.py
pytest -q

## Authors

Shrey Agarwal – Backend Developer
Yu-Kuang Chen – Backend Developer

```

```
