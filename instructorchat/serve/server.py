import os
import argparse
import trio
from trio_websocket import serve_websocket, ConnectionClosed, WebSocketConnection, WebSocketRequest
from typing import Final
import traceback
import json

from instructorchat.serve.inference import ChatIO, chat_loop

HOST: Final = "localhost"
PORT: Final = 6666

class NetworkChatIO(ChatIO):
    def __init__(self, connection: WebSocketConnection) -> None:
        self.connection = connection

    async def prompt_for_input(self, role: str) -> str:
        return await self.connection.get_message()

    async def prompt_for_output(self, role: str):
        pass

    async def display_output(self, output: str) -> None:
        await self.connection.send_message(json.dumps({"content": output}))

    async def stream_output(self, output_stream):
        output = ""
        async for chunk in output_stream:
            delta = chunk.choices[0].delta.content
            if delta:
                output += delta
                message = {"content": delta}
                await self.connection.send_message(json.dumps(message))

        await self.connection.send_message(json.dumps({}))
        return output

async def connect(request: WebSocketRequest):
    ws = await request.accept()

    try:
        async for _ in chat_loop(
            model_path="gpt-4o-mini",
            temperature=args.temperature,
            chatio=NetworkChatIO(ws),
            api_key=api_key,
        ):
            pass
    except ConnectionClosed:
        pass

async def main() -> None:
    await serve_websocket(connect, HOST, PORT, ssl_context=None) # Set ssl context for encryption

if __name__ == "__main__":
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