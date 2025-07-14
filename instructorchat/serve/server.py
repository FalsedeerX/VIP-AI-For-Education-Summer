import os
import argparse
import trio
from trio_websocket import serve_websocket, ConnectionClosed, WebSocketRequest
from typing import Final
from dotenv import load_dotenv
import traceback
import json

from instructorchat.serve.inference import (
    initialize_model,
    return_conversation,
    store_documents_action,
    generate_answer_action,
    ping
)

HOST: Final = "localhost"
PORT: Final = 6666

# Action dispatch dictionary for regular actions
ACTION_DISPATCH = {
    "return_conversation": return_conversation,
    "store_documents": store_documents_action,
    "ping": ping
}

# Streaming actions that handle their own messaging
STREAMING_ACTIONS = {
    "generate_answer": generate_answer_action
}


async def handle_websocket(request: WebSocketRequest):
    """Handle WebSocket connections with action-based dispatch."""
    ws = await request.accept()
    print("New WebSocket connection established")

    try:
        while True:
            message = await ws.get_message()
            print(f"[RECEIVED] {message}")

            try:
                payload = json.loads(message)
                action = payload.get("action")
                data = payload.get("data", {})

                # Handle streaming actions (they manage their own messaging)
                if action in STREAMING_ACTIONS:
                    await STREAMING_ACTIONS[action](data, websocket=ws)
                    continue

                # Handle regular actions
                if action not in ACTION_DISPATCH:
                    await ws.send_message(json.dumps({
                        "error": f"Unknown action: {action}",
                        "status": "error"
                    }))
                    continue

                # Call the corresponding function for regular actions
                result = await ACTION_DISPATCH[action](data, websocket=ws)

                # Only send result if the function didn't already send a message
                if result is not None:
                    await ws.send_message(json.dumps(result))

            except json.JSONDecodeError as e:
                await ws.send_message(json.dumps({
                    "error": f"Invalid JSON: {str(e)}",
                    "status": "error"
                }))
            except Exception as e:
                await ws.send_message(json.dumps({
                    "error": str(e),
                    "status": "error"
                }))

    except ConnectionClosed:
        print("WebSocket connection closed")


async def main() -> None:
    # Initialize the model before starting the server
    await initialize_model("gpt-4o-mini", api_key, args.temperature)
    print("Model initialized successfully")
    print(f"Starting WebSocket server on {HOST}:{PORT}")

    await serve_websocket(handle_websocket, HOST, PORT, ssl_context=None)

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--temperature", type=float, default=0.7)
    args = parser.parse_args()

    # Use API key from environment variable if not provided
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided either through --api-key or OPENAI_API_KEY environment variable")

    try:
        trio.run(main)
    except Exception as exc:
        traceback.print_exception(exc)
