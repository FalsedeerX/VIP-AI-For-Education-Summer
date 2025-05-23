# VIP-AI-For-Education-Summer
Codebase for our AI Teaching Assistant - VIP Team AI for Education

This file contains the latest REST API documentation for the endpoints.
Including the accepted methods and the expected returning data.

---

## Backend Internal Endpoints

### User Authentication

- `POST` `/api/login`
    > Performs user login, login information is embeded as `JSON` format.
    > Sample Request Content:
    ```json
    {
        "user_id": "chen5292",
        "password": "fakepasword123"
    }
    ```
    > If the credential is accepted, then it will retrun in status code `200` with content:
    ```json
    {
        "status": "Login Success"
    }
    ```
- `POST` `/api/logout`
- `POST` `/api/register`

### Chat Folders Mangement

- `GET` `api/folders`
- `POST` `api/organize`

### Chat Management

- `GET` `api/chat`
- `POST` `api/chat`
- `DELETE` `api/chat`
- `POST` `api/new_chat`


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

