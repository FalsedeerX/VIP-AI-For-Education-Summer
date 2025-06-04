# Session Manager Key Schema Design

---

## Key: `session:<token_uuid>`

- **Purpose**: Track each individual session token, and timeout automatically.
- **Auto Expire**: 10800 seconds
- **Datatype**: JSON

```json
{
	"username": "chen5292",
}
```

---

## Key: `user_sessions:<username>`

