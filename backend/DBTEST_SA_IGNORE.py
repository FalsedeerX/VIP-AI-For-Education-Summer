import psycopg
from psycopg import sql
from psycopg.errors import UniqueViolation
from argon2 import PasswordHasher

class DatabaseAgent:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn
        self.conn = psycopg.connect(self.dsn)
        self.ph = PasswordHasher()

    def register_user(self, username: str, email: str, password: str) -> int | None:
        """Create a new user, return its id or None if duplicate."""
        hashed = self.ph.hash(password)
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id", 
                        (username, email, hashed)
                    )
                    user_id = cur.fetchone()[0]
                    return user_id
        except UniqueViolation:
            return None
        
    def delete_user(self, username: str, password: str) -> int | None:
        hashed = self.ph.hash(password)
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, password FROM users WHERE username = %s",
                        (username,)
                    )
                    result = cur.fetchone()
                    if result is None:
                        return None
                    user_id, stored_hashed = result

                    try:
                        if not self.ph.verify(stored_hashed, password):
                            return None
                    except Exception:
                        return None
                    
                    cur.execute(
                        "DELETE FROM users WHERE id = %s RETURNING id",
                        (user_id,)
                    )
                    
                    deleted = cur.fetchone()
                    return deleted[0] if deleted else None


        except UniqueViolation:
            return None
        
if __name__ == "__main__":
    db = DatabaseAgent("postgres://shrey_agarwal:password@localhost:5432/purduegptdb")
    new_id = db.delete_user("alice", "password123")
    print("Old user ID:", new_id)
