# WebSocket Server Documentation

---

## Overview

This WebSocket server implements an action-based dispatch mechanism for handling different types of requests.  
The server supports four main actions: returning conversation history, storing documents, generating answers to questions with real-time streaming, and ping for connectivity testing.

---

## Features

- **Action-based dispatch**: All requests are handled through a JSON-based action system
- **Conversation management**: Maintains conversation history across requests
- **Document storage**: Store Python files from the KnowledgeBase directory for retrieval
- **Question answering**: Generate answers using context from stored documents with real-time streaming
- **Error handling**: Comprehensive error handling with status codes
- **CLI interface**: Command-line interface for direct interaction
- **Streaming responses**: Real-time streaming for answer generation

---

## API Actions

### Action - `return_conversation`

Retrieves the current conversation history.

**Request:**
```json
{
  "action": "return_conversation",
  "data": {}
}
```

**Response:**
```json
{
  "conversation": [
    {
      "role": "user",
      "content": "user message content"
    },
    {
      "role": "assistant", 
      "content": "assistant response content"
    }
  ],
  "status": "success"
}
```

---

### Action - `store_documents`

Stores a Python file from the KnowledgeBase directory for later retrieval and context generation.

**Request:**
```json
{
  "action": "store_documents",
  "data": {
    "file_path": "KnowledgeBase/your_file.py"
  }
}
```

**Response:**
```json
{
  "message": "File stored successfully",
  "status": "success"
}
```

**Note:** Only `.py` files are supported and must be located in the `KnowledgeBase` directory.

---

### Action - `generate_answer`

Generates an answer to a question with real-time streaming output using context from stored documents.

**Request:**
```json
{
  "action": "generate_answer",
  "data": {
    "question": "What is Python?",
    "folder": "optional_folder_path"
  }
}
```

**Streaming Response:**

1. **Stream chunks** (multiple messages):
```json
{
  "type": "stream_chunk",
  "content": "Python is a programming language...",
  "status": "streaming"
}
```

2. **Stream completion** (final message):
```json
{
  "type": "stream_complete",
  "answer": "Complete answer...",
  "contexts": [
    "Title: Context Title\nContext text content...",
    "Title: Another Context\nMore context content..."
  ],
  "status": "success"
}
```

---

### Action - `ping`

Simple ping-pong for testing connectivity.

**Request:**
```json
{
  "action": "ping",
  "data": {}
}
```

**Response:**
```json
{
  "result": "pong",
  "status": "success"
}
```

---

## Usage

### Starting the Server

```bash
# Using command line argument
python server.py --api-key YOUR_OPENAI_API_KEY --temperature 0.7

# Using environment variable
export OPENAI_API_KEY=your_api_key_here
python server.py --temperature 0.7

# Default temperature is 0.7 if not specified
```

---

### Command Line Interface (CLI)

For direct interaction without WebSocket:

```bash
# Basic usage
python cli.py --api-key YOUR_OPENAI_API_KEY

# With custom temperature
python cli.py --api-key YOUR_OPENAI_API_KEY --temperature 0.5

# With specific folder for context
python cli.py --api-key YOUR_OPENAI_API_KEY --folder /path/to/documents

# Using environment variable
export OPENAI_API_KEY=your_api_key_here
python cli.py
```

**CLI Commands:**
- `return conv` - Display current conversation
- `store <file_path>` - Store a Python file (e.g., `store KnowledgeBase/example.py`)
- `Ctrl+Z` (Windows) or `Ctrl+D` (Unix) - Exit the CLI

---

### Testing with the Test Client

```bash
# Install websockets if not already installed
pip install websockets

# Run the test client
python test_client.py
```

The test client demonstrates:
- Ping connectivity test
- Streaming answer generation
- Conversation retrieval
- Error handling

---

### WebSocket Connection

Connect to the WebSocket server at `ws://localhost:6666`

### Handling Streaming Responses

When using the `generate_answer` action, you'll receive multiple messages:

```javascript
// Example JavaScript client
const ws = new WebSocket('ws://localhost:6666');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'stream_chunk') {
        // Handle streaming chunk
        console.log('Chunk:', data.content);
        // Append to UI, etc.
    } else if (data.type === 'stream_complete') {
        // Handle completion
        console.log('Complete answer:', data.answer);
        console.log('Contexts:', data.contexts);
    } else {
        // Handle regular responses
        console.log('Response:', data);
    }
};

// Send streaming request
ws.send(JSON.stringify({
    action: 'generate_answer',
    data: { question: 'What is Python?' }
}));
```

---

## Error Handling

All responses include a `status` field:
- `"success"`: Action completed successfully
- `"error"`: Action failed, check the `error` field for details
- `"streaming"`: For streaming chunks (not final response)

Example error responses:
```json
{
  "error": "Question is required",
  "status": "error"
}
```

```json
{
  "error": "Only .py files are supported",
  "status": "error"
}
```

```json
{
  "error": "Model not initialized",
  "status": "error"
}
```

---

## Architecture

The server uses a global conversation object and action dispatch pattern:

1. **Global State**: Model and conversation are initialized once at startup using GPT-4o-mini
2. **Action Dispatch**: Each action is mapped to a corresponding async function
3. **Streaming Support**: All answer generation uses streaming for real-time responses
4. **JSON Protocol**: All communication uses JSON messages with `action` and `data` fields
5. **Error Handling**: Comprehensive error handling with proper status codes
6. **Retrieval System**: Uses ColPali embeddings and MongoDB for document storage and retrieval
7. **Context Integration**: Automatically retrieves relevant context from stored documents

---

## Dependencies

- `trio` and `trio-websocket` for WebSocket handling
- `openai` for GPT-4o-mini API integration
- `pymongo` for MongoDB document storage
- `pymupdf4llm` for PDF processing
- `instructorchat` modules for model handling and retrieval
- `websockets` for test client (optional)

---

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGO_URL`: MongoDB connection string (for document storage)

---

## File Structure

```
instructorchat/serve/
├── server.py          # WebSocket server implementation
├── inference.py       # Core inference and action handlers
├── cli.py            # Command-line interface
├── test_client.py    # WebSocket test client
└── README.md         # This documentation
``` 