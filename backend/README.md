# Database Schema Design

---

## Table - `user`
 
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

This will be holding data for every single folder,  
keeping track of the owner and the custom label for it.  

## Table - `folders`

```sql
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCE users(id),
    label TEXT NOT NULL
);
```

---

## Table - `chat_folder_map`

This table link the two entry from `chats` and `folder` table.

```sql
CREATE TABLE chat_folder_link (
    folder_id INT NOT NULL REFERENCE folders(id),
    chat_id  UUID NOT NULL REFERENCE chats(uid),
    PRIMARY KEY (folder_id, chat_id)
);
```

---

## Table - `chats`

```sql
```

