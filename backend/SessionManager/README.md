# Session Manager Key Schema Design

I am planning to design a SessionManager which can achieve some complex operation,  
such as:

- Auto purging **IDLE** session.
- Auto purging **expired** session.
- Auto extending **active** session.
- Prevent session token impersonate.

These features are intended to enhance user experience and ensure the website operates in a modern, efficient, and user-friendly manner.  

---

## Key: `session:<token_uuid>`

- **Purpose**: Track each individual session token, and timeout automatically.
- **Auto Expire**: 10800 seconds
- **Datatype**: `JSON`

```json
{
	"username": "chen5292",
	"ip_address": "203.0.113.10",
	"created_at": 1717523894.753216
}
```

---

## Key: `user_sessions:<username>`

- **Purpose**: Auto track the active session which belongs to a certain user.
- **Auto Expire**: Never
- **Datatype**: `ZSET`

```redis
ZADD user_sessions:chen5292 3600 8342684d-82c5-4cdb-9835-3ee9ae7ebf37
```