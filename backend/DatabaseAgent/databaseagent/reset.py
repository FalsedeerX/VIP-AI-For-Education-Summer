import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

def dump_every_table():
    load_dotenv(".env")
    db_host   = os.getenv("DB_HOST", "localhost")
    db_port   = int(os.getenv("DB_PORT", 5432))
    db_name   = os.getenv("DB_NAME")
    db_user   = os.getenv("DB_USER")
    db_passwd = os.getenv("DB_PASSWD")

    conn = psycopg.connect(
        f"postgresql://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_name}"
    )

    with conn.cursor() as cur:
        cur.execute("SET search_path TO chatbot;")

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT table_name
              FROM information_schema.tables
             WHERE table_schema = 'chatbot'
               AND table_type   = 'BASE TABLE'
             ORDER BY table_name;
        """)
        tables = [row["table_name"] for row in cur.fetchall()]

    for table in tables:
        print(f"\n\n===== TABLE: chatbot.{table} =====")
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM chatbot.{table} LIMIT 0;")
            column_names = [desc.name for desc in cur.description]
        print("COLUMNS:", column_names)

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"SELECT * FROM chatbot.{table} ORDER BY 1;")
            rows = cur.fetchall()

        if not rows:
            print("  [no rows]")
        else:
            for row in rows:
                print("  ", row)

    conn.close()

def reset_database():
    """
    Reset the database by dropping all tables in the public schema.
    This is a destructive operation and should be used with caution.
    """
    load_dotenv(".env")
    db_host   = os.getenv("DB_HOST", "localhost")
    db_port   = int(os.getenv("DB_PORT", 5432))
    db_name   = os.getenv("DB_NAME")
    db_user   = os.getenv("DB_USER")
    db_passwd = os.getenv("DB_PASSWD")

    conn = psycopg.connect(
        f"postgresql://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_name}"
    )

    with conn.cursor() as cur:
        cur.execute("SET search_path TO chatbot;")

    with conn.cursor() as cur:
        cur.execute("""
            TRUNCATE TABLE
              chat_folder_link,
              chat_messages,
              chats,
              folders,
              users
            RESTART IDENTITY CASCADE;
        """)
        conn.commit()

    conn.close()

if __name__ == "__main__":
    dump_every_table()
    reset_database()
    dump_every_table()
