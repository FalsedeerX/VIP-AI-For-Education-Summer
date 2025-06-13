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

- **Purpose**: Track each IP address origin of the session owner.
- **Auto Expire**: `Dynamic` (Default: `10800 Seconds`)
- **Datatype**: `Redis Key-String`

Sample Data:  

```redis
session:620dd3f3-b43c-4409-bd44-8f4fa0b7d3f0 → 127.0.0.1
```

---

## Key: `session_user:<token>`

- **Purpose**: Track the owner of a specific session token.
- **Auto Expire**: `Dynamic` (Default: `10800 Seconds`)
- **Datatype**: `Redis Key-String`

Sample Data:  

```redis
session_user:e6b47741-a3f7-43f0-b4e0-1ad14ba9e124 → chen5292
```

---

## Key: `user_sessions:<username>`

- **Purpose**: Auto track the active session which belongs to a certain user.
- **Auto Expire**: Never
- **Datatype**: `Redis ZSET (Sorted Lists)`

Query:  

```redis
ZADD user_sessions:chen5292 3600 8342684d-82c5-4cdb-9835-3ee9ae7ebf37
```

Sample Data:  

```redis
Key: "user_sessions"
|
├── Entry 1: 1728839201.500000 → "session:aaa111"
├── Entry 2: 1728839203.320000 → "session:bbb222"
├── Entry 3: 1728839211.654321 → "session:abc123"
├── Entry 4: 1728839250.000000 → "session:xyz999"

```