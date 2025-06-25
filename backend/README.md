# AI for Education Backend

This is the backend service for AI For Education, a chat-based application that helps users organize conversations by course and folder. It supports secure user authentication, asynchronous database operations, and modular service architecture.

---

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
|   ├── course_services.py   # Course creation, deletion and retrieval
│   ├── folder_services.py   # Folder creation, update, linking
│   └── user_services.py     # User auth, registration, validation
├── schemas/
│   ├── chat.py
│   ├── course.py
│   ├── folder.py
│   └── user.py
├── SessionManager/
│   └── session.py           # Session-based data management
├── Utils/
│   ├── mods/
│   │   ├── __init__.py
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
   ???

---

## Database Schema Design

Refer to the SQL definitions in the `/schemas` section above for how to initialize your tables.

- **users** — stores secure user accounts

- **courses** — allows chats/folders to be organized by course

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

#### `/users/me`

Action: `GET`  

Behavior: **Receive current username and the corresponding user ID.**  

Sample Request Body:  

None

Sample Response:  

```json
{
    "id": 6,
    "username": "chen5292"
}
```

---

#### `/users/auth`

Action: 'POST'

Behavior: **Verify user credential, if succeed a session token will be assigned.**

Sample Request Body:  

```json
{
    "username": "chen5292",
    "password": "apple123"
}
```

Sample Response:  

```json
true
```

---

#### `/users/register`

Action: `POST`

Behavior: **Register a new user in the database.**

Sample Request Body:  

```json
{
	"username": "chen5292",
    "email": "chen5292@purdue.edu",
    "password": "apple123"
}
```

Sample Response:

```json
true
```

---

#### `/users/delete`

Action: `DELETE`

Behavior: **Delete a user from the database, along with the chat history and folders.**

Sample Request Body:

```json
{
    "user_id": 6
}
```

Sample Response:

```raw
true
```

---

### ChatRouter

#### `/chats/create`

Action: `POST`  

Behavior: **Create a new chat for the current logged in user,  Returns newly created chat-id.**  

Sample Request Body:

```json
{
    "title": "How to prepare for exam ?"
}
```

Sample Response:

```json
"da22bd2a-a110-49ed-bc65-c18bc9ca8d8d"
```

---

#### `/chats/organize`

Action: `POST`

Behavior: **Organize a chat into a folder by `folder_id`. Will verify if the current token owner owns the specified chat and folder.**  

Sample Request Body:  

```json
{
    "folder_id": 12,
    "chat_id": "da22bd2a-a110-49ed-bc65-c18bc9ca8d8d"
}
```

Sample Response:

```json
true
```

---

#### `/chats/<chat_id>`

Action: `GET`  

Behavior: **Retrieve all messages associated with a specific chat.**

Sample Request Body:  

None

Sample Response:

```json
[
    {
        "user_id": 9,
        "message": "How to prepare for calulas exam 1 ?",
        "created_at": "2025-06-25T11:39:17.479368"
    },
    {
        "user_id": 9,
        "message": "What are some important formulas which I should know ?",
        "created_at": "2025-06-25T11:39:56.731342"
    },
    {
        "user_id": 9,
        "message": "Is the exam open book ?",
        "created_at": "2025-06-25T11:40:07.081901"
    }
]
```

---

#### `/chats/<chat-id>`

Action: `PUT`

Behavior: **Append a new message to the specified chat log.**

Sample Request Body:  

```json
{
    "message": "Is the exam open book ?"
}
```

Sample Response Body:

```json
true
```

---

#### `/chats/<chat-id>`

Action: `DELETE`

Behavior: **Delete a specified chat and the associated chat messages.**

Sample Request Body:

None

Sample Response:

```json
true
```

---

### FolderRouter

#### `/folders`

Action: `GET`

Behavior: **Get a list of chats which is organized in the specified folder.**  

Sample Request Body:  

```json
{
    "folder_id": 12
}
```

Sample Response:  

```json
{
    "How to prepare for exam ?": "4e61c2bb-7da0-4b0f-9e4c-cdb3498dc2f3",
    "Homework 2 Questions": "35ff37f5-1c2b-44f0-a3ad-c561072a45c2",
    "Exam Preparation Tips": "5ed48f9a-7df4-46dc-91ba-357dae9aa0d5",
    "Important Formulas for Calculus": "95d33a97-6871-49d8-89d2-700d5c2c9a2e"
}
```

---

#### `/folders/create`

Action: `POST`

Behavior: **Create a folder of a specified course for the current logged in user. Return newly created folder ID upon success.**

Sample Request Body:  

```json
{
    "folder_name": "Calculus Exam 1",
    "course_id": 1
}
```

Sample Response:  

```json
12
```

---

#### `/folders/organize`

Action: `POST`

Behavior: **Organize a folder into a course by `course_id`. Will verify whether the current user owns the specified folder.**

Sample Request Body:  

```json
{
    "folder_id": 12,
    "course_id": 1
}
```

Sample Response:  

```json
true
```

---

#### `/folders/delete`

Action: `DELETE`

Behavior: **Delete a folder and the associated chats and messages.**

Sample Request Body:  

```json
{
    "folder_id": 3
}
```

Sample Response:  

```json
true
```

---

### CourseRouter

#### `courses/`

Action: `GET`

Behavior: **Retrieve a list of `folders id` and the corresponding course title which the current user owns.**  

Sample Request Body:  

None

Sample Response:  

```json
{
    "Signals and Systems": [
        14,
        13
    ],
    "Object Oriented Programming with C++": [
        16,
        15
    ],
    "Probabilistic Methods": [
        17
    ]
}
```

---

#### `courses/create`

Action: `POST`

Behavior: **Create a new course in the database.**  

Sample Request Body:  

```json
{
    "course_code": "ECE36200",
    "course_title": "Microprocessor Systems and Interfacing"
}
```

Sample Response:  

```json
true
```

---

#### `courses/delete`

Action: `DELETE`

Behavior: **Delete a course and the associated folders, chats and messages.**

Sample Request Body:

```json
{
    "course_id": 2    
}
```

Sample Response:

```json
true
```

---

## Running Tests

pytest DatabaseAgent/test_database_agent.py  
pytest -q

---

## Authors

Shrey Agarwal – Backend Developer  
Yu-Kuang Chen – Backend Developer
