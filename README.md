# VIP-AI-For-Education-Summer

Codebase for our AI Teaching Assistant - VIP Team AI for Education

This file contains the latest REST API documentation for the endpoints.  
Including the accepted methods and the expected returning data.


---

## Backend Internal Endpoints

### User Authentication

- `POST` `/api/login`

    > Performs user login, login information is embeded as `JSON` format.  
    > Sample request content:  
    ```json
    {
        "user_id": "chen5292",
        "password": "fakepasword123"
    }
    ```
    > Returns following content with status code `200` upon success.  
    > Sample response content:
    ```json
    {
        "status": "Login Success."
    }
    ```

- `POST` `/api/logout`

    > Logout the current user and terminate session,   
    > no parameter is required for this request.  
    > Returns following content with status code `200` upon success.  
    > Sample request content:  
    ```json
    {
        "status": "Logout Success."
    }
    ```

- `POST` `/api/register`
    
    > Register new user, user information is embeded as `JSON` format.  
    > Sample requst content:
    ```json
    {
        "user_id": "Falsedeer",
        "password": "qwert123",
        "email": "chen5292@purdue.edu"
    }
    ```
    > Will accept the request only if the `user_id` doesn't exist in the current database.  
    > Returns following content with status code `200` upon success.
    > Sample response content:
    ```json
    {
        "status": "Register Success."
    }
    ```

### Chat Folders Mangement

- `GET` `api/folders`

    > Retrieve a list of user created folder in `JSON` format,  
    > no parameter is required for this request, returns status code `200` upon success.  
    > Sample response content:
    ```json
    {
        "Exam 1": ["3b6b4b2f-c8e2-4c39-92e3-242317d5f50b", "1d7fdf44-574a-4476-b124-4f1d896a5e6b"],
        "Exam 2": ["d55b4db5-e/a39-45f2-8a6f-746108b9e6c6", "5f356b9e-9691-4fe3-8fd8-1b70b8dc3b78"],
        "Assignment 1": ["2f9e69c6-63fa-4037-a712-6ff7a30909f8"]
    }
    ```

- `POST` `api/organize`

    > Organize a chat-id to a specified folder,  
    > source and destination information are embeded as `JSON` format.  
    > Sample request content:  
    ```json
    {
        "chat_id": "0c3cc39a-18cf-4d94-a1c7-690a58596a0e",
        "folder": "Exam 1"
    }
    ```
    > Returns following content with status code `200` upon success.  
    > Sample response content:  
    ```json
    {
        "status": "Organize Success."
    }
    ```

### Chat Management

- `GET` `api/chat`

    > Retrieve a chat's history in `JSON` format,  
    > parameters required for this operation is passed directly in the URL.  
    > Sample request:  
    ```http
    GET http://127.0.0.1/api/chat?id=4d6f4b40-29e6-4e4e-91b5-93d3c14b06a0
    ```
    > Sample response:  
    ```json
    [
        {
            "message": "How are you ?",
            "sender": "chen5292",
            "timestamp": 1716481200.000
        },
        {
            "message": "I am fine, thank you !",
            "sender": "Purdue-GPT",
            "timestamp": 1716481320.000
        },
        {
            "message": "How is the weather like in Lafayette ?",
            "sender": "chen5292",
            "timestamp": 1716481440.000
        },
        {
            "message": "It will probably rain in the afternoon !!",
            "sender": "Purdue-GPT",
            "timestamp": 1716481560.000
        }
    ]
    ```

- `POST` `api/chat`

    > Log a single chat entry to the database, message details are embeded as `JSON` format.  
    > Sample request content:
    ```json
    {
        "chat_id": "b91b2e63-0e30-4cf1-8b75-6ec34fef63cf",
        "sender": "Purdue-GPT",
        "message": "Can you read me ?"
    }
    ``` 
    > Returns following content with status code `200` upon success.  
    > Sample response content:  
    ```json
    {
        "status": "Log Success."
    }
    ```


- `DELETE` `api/chat`

    > Delete a specified chat by its `UUID`, target information is embeded as `JSON` format.  
    > Sample request content:  
    ```json
    {
        "chat_id": "bd7806a3-d61e-42ab-bc84-8fa5a1e1f169"
    }
    ```
    > Returns following content with status code `200` upon success.  
    ```json
    {
        "status": "Deletion Success."
    }
    ```

- `POST` `api/new_chat`

    > Create a new chat and return the chat-id in `JSON` format,  
    > no parameter is required for this request, return status code `200` upon success.  
    > Sample response content:  
    ```json
    {
        "chat_id": "4abf51c1-9849-4f0f-9e9a-e460edcb7e02"
    }
    ```

---

AI Model Processing
- GET /chat
    > Post an query to the AI model, the model output will be included in the content of the response.
- GET /chat/history
    > Retrieve the list of chat history. (Probably in XML or JSON)
- POST /chat/folders
    > Retrieve the list of chat folders. (Probably in XML or JSON)
- POST /chat/classify
    > Update the folder classification to a specific folder.

