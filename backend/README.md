# Database Schema Design

## Table - `user`

Password will be hashed in `Argon2` before storage,  
user authentication system will be comparing hashes rather than plaintext password.  

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```


