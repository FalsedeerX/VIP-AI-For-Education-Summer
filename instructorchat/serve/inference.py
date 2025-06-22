"""Inference for GPT-4-mini model."""
import abc
import openai
from typing import Dict, Optional
import logging
import uuid
from datetime import datetime, timezone

from instructorchat.model.model_adapter import load_model, get_model_adapter
from instructorchat.conversation import get_conv_template
from instructorchat.retrieval.search_with_chromadb import retrieve_relevant_context

class ChatIO(abc.ABC):
    @abc.abstractmethod
    async def prompt_for_input(self, role: str) -> str:
        """Prompt for input from a role."""

    @abc.abstractmethod
    async def prompt_for_output(self, role: str):
        """Prompt for output from a role."""

    @abc.abstractmethod
    async def display_output(self, output: str):
        """Display output to user."""

async def generate_response(params: Dict) -> str:
    """Generate response using OpenAI API."""
    try:
        client = openai.AsyncOpenAI(api_key=openai.api_key)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=params["messages"],
            temperature=0.7,
            stream=False,  # Disable streaming
        )

        if not response or not response.choices:
            return "Error: Empty response from API"

        return response.choices[0].message.content

    except Exception as e:
        print("hi,error roi nayy")
        return f"Error: {str(e)}"

async def chat_loop(
    model_path: str,
    temperature: float,
    chatio: ChatIO, #chatio is a chosen I/O handlings, while ChatIO (abstract) defines how every type of I/O handlings should look like.
    api_key: Optional[str] = None,
):
    """Main chat loop."""
    # Set API key
    if api_key:
        openai.api_key = api_key
    elif not openai.api_key:
        raise ValueError("OpenAI API key must be provided")

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)

    # Load model
    adapter = get_model_adapter(model_path)
    load_model(model_path, api_key)
    conv = adapter.get_default_conv_template(model_path)

    while True:
        inp = await chatio.prompt_for_input(conv.roles[0])

        # Handle commands
        if inp == "return conv":
            print(conv.get_message())
            continue

        if inp.startswith("store "):
            try:
                file_path = inp.split("store ")[1].strip()
                if not file_path.endswith('.py'):
                    logger.error("Only .py files are supported")
                    continue

                logger.info(f"Storing file: {file_path}")
                from instructorchat.retrieval.store_with_mongodb import store_documents

                success, message = store_documents(file_path)
                if success:
                    logger.info(message)
                else:
                    logger.error(message)
            except ImportError as e:
                logger.error(f"Error importing store module: {str(e)}")
            except Exception as e:
                logger.error(f"Error storing file: {str(e)}")
            continue

        if not inp:
            print("exit...")
            break

        # Get relevant context for the query
        contexts = await retrieve_relevant_context(inp, api_key)

        # Prepare the prompt with context
        context_text = "\n\n".join([
            f"From {ctx['title']}:\n{ctx['content']}"
            for ctx in contexts
        ])

        # Format the message with context and question
        formatted_message = f"""
            Here is the question: <QUESTION> {inp} </QUESTION>

            The following are the contexts:
            <CONTEXT>
            {context_text}
            </CONTEXT>"""

        # Add messages to conversation
        conv.append_message(conv.roles[0], formatted_message)

        # Create the final prompt with context
        messages = conv.to_openai_api_messages()

        gen_params = {
            "messages": messages,
            "temperature": temperature
        }

        response = await generate_response(gen_params)
        #Add response to complete a question-response pair
        conv.append_message(conv.roles[1], response)

        # Update conversation and display response
        # conv.update_last_message(response.strip())
        await chatio.display_output(response.strip())
