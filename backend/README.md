# AI for Education Backend

This is the backend service for AI For Education, a chat-based application that helps users organize conversations by course and folder. It supports secure user authentication, asynchronous database operations, and modular service architecture.

---

## Project Structure

```txt
backend/
├── DatabaseAgent/
│   ├── database_async.py    # Async PostgreSQL connection & methods
│   ├── reset.py             # Script to clear/truncate tables and to view current db
│   └── test_database_agent.py
├── services/
│   ├── chat_services.py     # Logic for chat handling
│   ├── course_services.py   # Course creation, deletion and retrieval
│   ├── folder_services.py   # Folder creation, update, linking
│   ├── user_services.py     # User auth, registration, validation
│   ├── websocket.py
│   │   ├── chat.py
│   │   ├── course.py
│   │   ├── folder.py
│   │   └── user.py
├── SessionManager/
│   └── session.py           # Session-based data management
├── Utils/
│   ├── mods/
│   │   └── hd.py            # HexDump module for connection debugging.
│   └── echo_server.py
├── backend.py               # FastAPI app entry point
└── requirements.txt         # Python dependencies
```

---

## Core Features

- Secure User Authentication using Argon2 hashing.
- Organized Conversations by folders and courses.
- Asynchronous interactions with PostgreSQL.
- Testable Design with isolated services and schema layers.
- UUID-based Chat Linking with folder associations.
- Modern and secure session mangement solution.

---

## Getting Started

1. Clone the Repository
   git clone
   cd backend
2. Install Dependencies
   pip install -r requirements.txt
3. Setup Environment
   Create a .env file in the root directory with:

   - DB_HOST=localhost
   - DB_PORT=5432
   - DB_NAME=yourdbname
   - DB_USER=yourdbuser
   - DB_PASSWD=yourdbpass

4. Run the Server
   ```txt
   python backend.py
   ```

---

## Database Schema Design

Refer to the SQL definitions in the `/schemas` section above for how to initialize your tables.

- **users** — stores secure user accounts

- **courses** — allows chats and folders to be organized by course

- **folders** — user defined containers for chat threads

- **chat_folder_link** — many-to-many link between chats and folders

- **chats** — contains metadata for each chat thread

- **chat_messages** — logs every user/bot message

See the full schema here [Database Agent Docs](/backend/DatabaseAgent/README.md)

---

## Session Managment

This backend uses a custom session system powered by Redis to manage user logins.
Each authenticated user receives a unique UUID token tied to their IP address.
A background worker monitors session activity and:

- Session token impersonate prevention.
- Expires tokens after inactivity or TTL timeout.
- Allows session verification and extension via service methods.

See the more on session managment [Session Manager Docs](/backend/SessionManager/README.md),
this system supports multi-session tracking, secure IP validation, and idle cleanup.

---

## Endpoints API

### UserRouter

#### /users/me

Action: GET
Behavior: Returns the currently authenticated user’s ID, username, and admin status.

Sample Request Body:
None

Sample Response:

```txt
{
    "id": 6,
    "username": "chen5292",
    "admin": false
}
```

#### /users/auth

Action: POST
Behavior: Verify user credentials and assign a session token via cookie.

Sample Request Body:

```txt
{
    "username": "chen5292",
    "password": "apple123"
}
```

Sample Response:

```txt
true
```

#### /users/register

Action: POST
Behavior: Register a new user with a username, email, and password.

Sample Request Body:

```txt
{
    "username": "chen5292",
    "email": "chen5292@purdue.edu",
    "password": "apple123",
    "is_admin": false
}
```

Sample Response:

```txt
true
```txt

#### /users/delete

Action: DELETE
Behavior: Delete a user from the database (requires session verification).

Sample Request Body:
```txt
{
    "user_id": 6
}
```

Sample Response:

```txt
true
```

#### /users/logout

Action: POST
Behavior: Logout the user by invalidating the session token and removing the cookie.

Sample Request Body:
None

Sample Response:

```txt
true
```

#### /users/joincourse

Action: POST
Behavior: Add a course to the current user’s list using the course code.

Sample Request Body:

```txt
{
    "course_code": "CS180"
}
```

Sample Response:

```txt
true
```

#### /users/deletecourse

Action: POST
Behavior: Remove a course from the current user’s course list.

Sample Request Body:

```txt
{
    "course_code": "CS180"
}
```

Sample Response:

```txt
true
```

#### /users/getcourses

Action: GET
Behavior: Retrieve the list of course codes the current user is enrolled in.

Sample Request Body:
None

Sample Response:

```txt
[
    {
        "course_code": "CS180"
    },
    {
        "course_code": "ECE301"
    }
]
```

### FolderRouter

#### /folders

Action: POST
Behavior: Retrieve a list of chats inside a specific folder by folder_id.

Sample Request Body:

```txt
{
    "folder_id": 12
}
```

Sample Response:

```txt
[
    {
        "chat_id": "da22bd2a-a110-49ed-bc65-c18bc9ca8d8d",
        "title": "Exam Review"
    }
]
```

#### /folders/create

Action: POST
Behavior: Create a folder within a course (admin only). Returns newly created folder ID.

Sample Request Body:

```txt
{
    "folder_name": "Finals Prep",
    "course_id": 3
}
```

Sample Response:

```txt
12
```

#### /folders/delete

Action: DELETE
Behavior: Delete a folder and associated chats. Requires session verification.

Sample Request Body:

```txt
{
    "folder_id": 12
}
```

Sample Response:

```txt
true
```

#### /folders/organize

Action: POST
Behavior: Organize a folder into a course using course_id.

Sample Request Body:

```txt
{
    "folder_id": 12,
    "course_id": 3
}
```

Sample Response:

```txt
true
```

### CourseRouter

#### /courses

Action: GET
Behavior: Retrieve courses and folder IDs for the current user.

Sample Request Body:
None

Sample Response:

```txt
{
    "CS180": [12, 13],
    "ECE301": [15]
}
```

#### /courses/create

Action: POST
Behavior: Create a new course with course code and title. Returns course ID.

Sample Request Body:

```txt
{
    "course_code": "PHYS241",
    "course_title": "Electricity and Magnetism"
}
```

Sample Response:

```txt
7
```

#### /courses/delete

Action: DELETE
Behavior: Delete a course and all related folders and chats.

Sample Request Body:

```txt
{
    "course_id": 7
}
```

Sample Response:

```txt
true
```

#### /courses/get

Action: POST
Behavior: Retrieve all folders associated with a specific course.

Sample Request Body:

```txt
{
    "course_id": 7
}
```

Sample Response:

```txt
[
    {
        "chat_id": "1e4d8bfc-7eb1-42fc-ae0f-1c982ea10926",
        "title": "Midterm Topics"
    }
]
```

### ChatRouter

#### /chats/create

Action: POST
Behavior: Create a new chat for the current logged in user. Returns the newly created chat ID.

Sample Request Body:

```txt
{
"title": "Preparing for midterm"
}
```

Sample Response:

```txt
"27b540c7-3e47-4c3c-b28f-b3c33b45b4f3"
```

#### /chats/random

Action: GET
Behavior: Retrieve a random chat ID belonging to the current user.

Sample Request Body:
None

Sample Response:

```txt
"da22bd2a-a110-49ed-bc65-c18bc9ca8d8d"
```

#### /chats/organize

Action: POST
Behavior: Organize a chat into a folder. Verifies ownership of both chat and folder.

Sample Request Body:

```txt
{
"chat_id": "da22bd2a-a110-49ed-bc65-c18bc9ca8d8d",
"folder_id": 12
}

```txt

Sample Response:
```txt
true
```

#### /chats/{chat_id}

Action: GET
Behavior: Retrieve all messages associated with a specific chat.

Sample Request Body:
None

Sample Response:

```txt
[
{
"user_id": 9,
"message": "What topics are covered in the exam?",
"created_at": "2025-07-11T10:23:00.000000"
}
]
```txt

#### /chats/delete/{chat_id}

Action: DELETE
Behavior: Delete a specific chat, after verifying user owns it.

Sample Request Body:
None

Sample Response:
```txt
true
```

#### /chats/owner/{chat_id}

Action: GET
Behavior: Return the owner_id of the specified chat.

Sample Request Body:
None

Sample Response:

```txt
{
"owner_id": 6
}
```

#### /chats/relay/{chat_id}

Action: WebSocket
Behavior: Relay real-time user messages and AI-generated responses via a WebSocket stream.
Authentication is disabled on this endpoint due to cross-origin cookie issues.

## Running Tests

Important notes:
Runs out of order  
Requires backend to ve running  
Needs cookie to be set "secure=False" In user_services.py

```txt
pytest DatabaseAgent/test_database_agent.py
pytest -q
```

---

## Authors

Shrey Agarwal  
Yu-Kuang Chen
