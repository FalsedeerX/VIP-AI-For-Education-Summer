# Database Schema Design

## Table - `user`

A new change in the schema:  
all user will be refernced by their unique `SERIAL` `id` instead of the original `TEXT` `username`,  
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


