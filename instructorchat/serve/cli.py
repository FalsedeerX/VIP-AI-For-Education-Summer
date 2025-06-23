"""
Chat with GPT-4o-mini using command line interface.

Usage:
python3 cli.py --api-key YOUR_API_KEY
"""
import argparse
import os
import traceback
import trio
from typing import Optional

from instructorchat.serve.inference import ChatIO, chat_loop

class SimpleChatIO(ChatIO):
    def __init__(self):
        self.prompt = "User: "
        self.output_prefix = "Assistant: "

    async def prompt_for_input(self, role: str) -> str:
        """Get input from user."""
        prompt_data = []
        line = input(f"{role} : ")
        while True: # helps collect multi-line inputs.
            prompt_data.append(line.strip())
            try:
                line = input()
            except EOFError as e: # only ends loop when user signals end of input | Ctrl+Z on Windows
                break
        return "\n".join(prompt_data)

    async def prompt_for_output(self, role: str):
        """Prompt for output."""
        print(self.output_prefix, end="", flush=True)

    async def display_output(self, output: str):
        """Display output to user."""
        print(f"assistant :", output)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--temperature", type=float, default=0.7)
    args = parser.parse_args()

    # Use API key from environment variable if not provided
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided either through --api-key or OPENAI_API_KEY environment variable")

    chatio = SimpleChatIO()
    try:
            # Same thing as await but has to be implemented this way because I need to use yield for evaluations
            async for _ in chat_loop(
                model_path="gpt-4o-mini",
                temperature=args.temperature,
                chatio=chatio,
                api_key=api_key,
            ):
                pass

            return None
    except KeyboardInterrupt:
        print("exit...")

if __name__ == "__main__":
    try:
        trio.run(main)
    except Exception as exc:
        traceback.print_exception(exc)