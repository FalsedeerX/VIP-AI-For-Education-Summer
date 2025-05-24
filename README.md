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
    > Returns following content with status code `200` upon success.  
    ```json
    {
        "status": "Login Success"
    }
    ```
- `POST` `/api/logout`
    > Logout the current user and terminate session,   
    > no parameter is required for this operation.  
    > Returns following content with status code `200` upon success.  
    ```json
    {
        "status": "Logout Success"
    }
    ```
- `POST` `/api/register`
    > Register new user, user information is embeded as `JSON` format.
    ```json
    {
        "user_id": "Falsedeer",
        "password": "qwert123",
        "email:" "chen5292@purdue.edu"
    }
    ```
    > Will accept the request only if the `user_id` doesn't exist in the current database.  
    > Returns following content with status code `200` upon success.
    ```json
    {
        "status": "Register Success"
    }
    ```

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

