"""
Chat with GPT-4-mini using command line interface.

Usage:
python3 cli.py --api-key YOUR_API_KEY
"""
import argparse
import os
import traceback
import trio

from instructorchat.serve.inference import ChatIO, chat_loop
from instructorchat.evaluation.evaluate import get_responses, run_evaluations

class SimpleChatIO(ChatIO):
    async def prompt_for_input(self, role) -> str:
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
        print(f"{role}: ", end="", flush=True)

    async def stream_output(self, output_stream):
        output = ""
        async for chunk in output_stream:
            delta = chunk.choices[0].delta.content
            if delta:
                output += delta
                print(delta, end="", flush=True)

        print()

        return output

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--eval", type=str, default=argparse.SUPPRESS) # Get responses and evaluate
    parser.add_argument("--eval-responses", type=str, default=argparse.SUPPRESS) # Evaluate existing responses file
    args = parser.parse_args()

    # Use API key from environment variable if not provided
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided either through --api-key or OPENAI_API_KEY environment variable")

    chatio = SimpleChatIO()
    try:
        if "eval" in args:
            if "eval_responses" in args:
                raise ValueError("Only one of 'eval' and 'eval-responses' should be provided")

            responses_file = await get_responses(
                model_path="gpt-4o-mini",
                temperature=args.temperature,
                chatio=chatio,
                api_key=api_key,
                input_file=args.eval if args.eval is not None else "tests.json"
            )

            return responses_file
        elif "eval_responses" in args:
            return args.eval_responses if args.eval_responses is not None else "responses.json"
        else:
            await chat_loop(
                model_path="gpt-4o-mini",
                temperature=args.temperature,
                chatio=chatio,
                api_key=api_key,
            )

            return None
    except KeyboardInterrupt:
        print("exit...")

if __name__ == "__main__":
    try:
        eval_responses = trio.run(main)

        if eval_responses is not None:
            run_evaluations(eval_responses)
    except ExceptionGroup as exc:
        traceback.print_exception(exc)