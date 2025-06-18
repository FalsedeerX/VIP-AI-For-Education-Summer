## DESC: Database Reset/Initialize File with Entry Samples
## Coded by Falsedeer (Yu-Kuang Chen)
## CopyRight (C) All Rights Reserved

from tinydb import TinyDB, Query


if __name__ == "__main__":
    # open the connection and truncate all entry in all tables
    db = TinyDB("database.json")
    for table in db.tables():
        db.table(table).truncate()

    # initialize dummy user entry in table `users`
    users_table = db.table("users")
    users_table.insert({"user_id": "chen5292", "email": "chen5292@purdue.edu", "password": "apple123"})
    users_table.insert({"user_id": "chou610", "email": "chou610@purdue.edu", "password": "banana666"})

    # initialize dummy login session entry in table `sessions`
    sessions_table = db.table("sessions")
    sessions_table.insert({"token": "27aeeb13-a72c-45f6-90eb-bc97fbb36767", "user_id": "chen5292", "expires_at": 1741745471.295948})

    # initialize dummy char folders in table `chat_folders`
    chat_folders_table = db.table("chat_folders")
    chat_folders_table.insert({"user_id": "chen5292", "folders": [{"label": "Assignment 1", "chat_ids": []}, {"label": "Assignment 2", "chat_id": []}]})
    chat_folders_table.insert({"user_id": "chou610", "folders": [{"label": "Assignment 1", "chat_ids": ["5439494f-b9be-4f81-b242-56eecc8c1841"]}, {"label": "Assignment 2", "chat_id": []}]})

    # initialize chat history in table 'chat_logs'
    chat_logs_table = db.table("chat_logs")
    chat_logs_table.insert({"chat_id": "5439494f-b9be-4f81-b242-56eecc8c1841",
                            "user_id": "chou610",
                            "messages": [
                                            {"timestamp": 1741287392.308209, "sender": "chen5292", "message": "How are you ?"},
                                            {"timestamp": 1741287392.308209, "sender": "AI-Model", "message": "I am fine, thank you !"},
                                            {"timestamp": 1741287392.308209, "sender": "chen5292", "message": "How is the weather like in Lafayette ?"},
                                            {"timestamp": 1741287395.279668, "sender": "AI-Model", "message": "It will probably rain in the afternoon !!"}
                                        ]
                            })

    chat_logs_table.insert({
                            "chat_id": "9304466d-2b24-4a31-af76-5812a7289933",
                            "user_id": "chen5292",
                            "messages": []
                            })

    # dump the whole database
    print("[Table Dump]:\n{}\n".format(db.tables()))

    # dump all the entry in all tables
    for table in db.tables():
        print("[Table] {}:\n{}\n".format(table, db.table(table).all()))
