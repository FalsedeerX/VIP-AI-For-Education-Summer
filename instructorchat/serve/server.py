import os
import argparse
import trio
from trio_websocket import serve_websocket, ConnectionClosed, WebSocketConnection, WebSocketRequest
from typing import Final
import traceback

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

    async def stream_output(self, output_stream):
        # pre = 0
        # for outputs in output_stream:
        #     output_text = outputs["text"]
        #     print(output_text[pre:], end="", flush=True)
        #     pre = len(output_text)
        # print()
        # return output_text

        # output_stream = ""
        # for chunk in output_stream:
        #     print(chunk["text"], end="", flush=True)
        #     output_stream += chunk["text"]
        output = output_stream.choices[0].message.content
        await self.connection.send_message(output)
        return output

    async def print_output(self, text: str):
        pass

async def connect(request: WebSocketRequest):
    ws = await request.accept()

    try:
        await chat_loop(
            model_path="gpt-4o-mini",
            temperature=args.temperature,
            chatio=NetworkChatIO(ws),
            api_key=api_key,
        )
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
    except ExceptionGroup as exc:
        traceback.print_exception(exc)