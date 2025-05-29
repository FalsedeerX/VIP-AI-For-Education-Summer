# Database Schema Design

---

## Table - `users`
 
From now on, all user will be refernced by their unique `SERIAL` `id` instead of the original `TEXT` `username`,  
in order to reduce the risk of performing an injection attack by using special username.  
User password will be hashed with **Argon2** before storage,  
authentication system will verify user by comparing hashes rather than plaintext.  

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Table - `courses`

```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Table - `folders`

This will be holding data for every single folder,  
keeping track of the owner and the custom label for it.  

```sql
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    course_id INT NOT NULL REFERENCES courses(id),
    user_id INT NOT NULL REFERENCES users(id),
    course_id INT NOT NULL REFERENCES course(id),
    label TEXT NOT NULL
);
```

---

## Table - `chat_folder_link`

This table link the two entry from `chats` and `folder` table.

```sql
CREATE TABLE chat_folder_link (
    folder_id INT NOT NULL REFERENCES folders(id),
    chat_id  UUID NOT NULL REFERENCES chats(id),
    PRIMARY KEY (folder_id, chat_id)
);
```

---

## Table - `courses`

Using collection of chat folders to create a group of course.  

```sql
CREATE TABLE course (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
```

---

## Table - `chats`

```sql
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Table - `chat_messages`

All users message and chatbot response will be stored in this table,  
message rotation logic should be implemented in the backend to prevent unbounded database growth.

```sql
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    chat_id UUID NOT NULL REFERENCES chats(id),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---
