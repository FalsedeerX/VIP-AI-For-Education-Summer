"""Inference for GPT-4-mini model."""
from openai import AsyncStream
from openai.types.chat import ChatCompletionChunk
from typing import Dict, Optional, List, Any
from PIL import Image
import traceback
import abc
import openai
import logging
import json

from instructorchat.model.model_adapter import load_model, get_model_adapter
from instructorchat.retrieval.search import retrieve_relevant_context
from instructorchat.conversation import Message, Role

# Global conversation object for action-based dispatch
global_conv = None
global_api_key = None
global_temperature = 0.7


class ChatIO(abc.ABC):
    @abc.abstractmethod
    async def prompt_for_input(self, role: Role) -> str:
        """Prompt for input from a role."""

    @abc.abstractmethod
    async def prompt_for_output(self, role: Role) -> None:
        """Prompt for output from a role."""

    @abc.abstractmethod
    async def display_output(self, output: str) -> None:
        """Display output to user."""

    @abc.abstractmethod
    async def stream_output(self, output_stream: AsyncStream[ChatCompletionChunk]) -> str:
        pass


async def ping(data = None, websocket = None):
    if websocket:
        await websocket.send_message(json.dumps({"result": "pong", "status": "success"}))
    else:
        return {"result": "pong", "status": "success"}


async def initialize_model(model_path: str, api_key: str, temperature: float):
    """Initialize the global model and conversation."""
    global global_conv, global_api_key, global_temperature

    global_api_key = api_key
    global_temperature = temperature

    # Set API key
    openai.api_key = api_key

    # Load model
    adapter = get_model_adapter(model_path)
    load_model(model_path, api_key)
    global_conv = adapter.get_default_conv_template(model_path)


async def return_conversation(data: Dict, websocket = None) -> Dict:
    """Action: Return the current conversation."""
    global global_conv

    if global_conv is None:
        if websocket:
            await websocket.send_message(json.dumps({"error": "Model not initialized", "status": "error"}))
        return {"error": "Model not initialized"}

    convo = global_conv.get_messages()

    if websocket:
        await websocket.send_message(json.dumps({"conversation": convo, "status": "success"}))
        return None  # Don't send twice

    return {
        "conversation": convo,
        "status": "success"
    }


async def store_documents_action(data: Dict, websocket = None) -> Dict:
    """Action: Store documents from file path."""
    global global_api_key

    if global_api_key is None:
        if websocket:
            await websocket.send_message(json.dumps({"error": "Model not initialized", "status": "error"}))
        return {"error": "Model not initialized"}

    try:
        file_path = data.get("file_path", "")
        if not file_path.endswith('.py'):
            if websocket:
                await websocket.send_message(json.dumps({"error": "Only .py files are supported", "status": "error"}))
            return {"error": "Only .py files are supported"}

        from instructorchat.retrieval.store import store_documents

        success, message = store_documents(file_path)

        if websocket:
            if success:
                await websocket.send_message(json.dumps({"message": message, "status": "success"}))
            else:
                await websocket.send_message(json.dumps({"error": message, "status": "error"}))
            return None  # Don't send twice

        if success:
            return {"message": message, "status": "success"}
        else:
            return {"error": message, "status": "error"}

    except ImportError as e:
        error_msg = f"Error importing store module: {str(e)}"
        if websocket:
            await websocket.send_message(json.dumps({"error": error_msg, "status": "error"}))
        return {"error": error_msg, "status": "error"}
    except Exception as e:
        error_msg = f"Error storing file: {str(e)}"
        if websocket:
            await websocket.send_message(json.dumps({"error": error_msg, "status": "error"}))
        return {"error": error_msg, "status": "error"}


async def generate_answer_action(data: Dict, websocket=None):
    """Action: Generate answer for a question with streaming output."""
    global global_conv, global_api_key, global_temperature

    if global_conv is None or global_api_key is None:
        if websocket:
            await websocket.send_message(json.dumps({"error": "Model not initialized", "status": "error"}))
        return {"error": "Model not initialized"}

    try:
        question = data.get("question", "")
        if not question:
            if websocket:
                await websocket.send_message(json.dumps({"error": "Question is required", "status": "error"}))
            return {"error": "Question is required", "status": "error"}

        # Get relevant context for the query
        contexts = await retrieve_relevant_context(question, global_api_key, folder=data.get("folder", None))

        # Prepare the prompt with context
        context_text = "\n\n".join([
            f"Title: {ctx['title']}\n{ctx['text']}"
            for ctx in contexts
        ])

        # Format the message with context and question
        formatted_message = f"""
            Here is the question: <QUESTION> {question} </QUESTION>

            The following are the contexts:
            <CONTEXT>
            {context_text}
            </CONTEXT>"""

        # Add messages to conversation
        global_conv.append_message(Message("user").add_text(formatted_message))

        # Create the final prompt with context
        messages = global_conv.to_openai_api_messages()

        gen_params = {
            "messages": messages,
            "temperature": global_temperature
        }

        # Generate streaming response
        stream = await generate_response_stream(gen_params)

        if stream is None:
            if websocket:
                await websocket.send_message(json.dumps({"error": "Failed to generate stream", "status": "error"}))
            return {"error": "Failed to generate stream", "status": "error"}

        # Stream the response
        full_response = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                if websocket:
                    # Send streaming chunk
                    await websocket.send_message(json.dumps({
                        "type": "stream_chunk",
                        "content": delta,
                        "status": "streaming"
                    }))

        # Add complete response to conversation
        global_conv.append_message(Message("assistant").add_text(full_response.strip()))

        # Send completion signal
        if websocket:
            await websocket.send_message(json.dumps({
                "type": "stream_complete",
                "answer": full_response,
                "contexts": [f"Title: {ctx['title']}\n{ctx['text']}" for ctx in contexts],
                "status": "success"
            }))

        return {
            "answer": full_response,
            "contexts": [f"Title: {ctx['title']}\n{ctx['text']}" for ctx in contexts],
            "status": "success"
        }

    except Exception as e:
        error_msg = f"Error generating answer: {str(e)}"
        if websocket:
            await websocket.send_message(json.dumps({"error": error_msg, "status": "error"}))
        return {"error": error_msg, "status": "error"}


async def generate_response_stream(params: Dict):
    """Stream response using OpenAI API."""
    try:
        client = openai.AsyncOpenAI(api_key=global_api_key)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=params["messages"],
            temperature=params["temperature"],
            stream=True,
        )

        if not response:
            print("Error: Empty response from API")
            return None

        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


async def chat_loop(
    model_path: str,
    temperature: float,
    chatio: ChatIO,  # chatio is a chosen I/O handlings, while ChatIO (abstract) defines how every type of I/O handlings should look like.
    api_key: Optional[str] = None,
    evaluation_test_cases: Optional[List[Dict[str, Any]]] = None,
    folder: Optional[str] = None
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

    if evaluation_test_cases:
        logger.info("Running chat loop in evaluation mode")

    # Load model
    adapter = get_model_adapter(model_path)
    load_model(model_path, api_key)
    conv = adapter.get_default_conv_template(model_path)

    idx = 0

    while True:
        inp = evaluation_test_cases[idx]["input"] if evaluation_test_cases else await chatio.prompt_for_input("user")

        # Handle commands
        if inp == "return conv":
            print(conv.get_messages())
            continue

        if inp.startswith("store "):
            try:
                file_path = inp.split("store ")[1].strip()
                if not file_path.endswith('.py'):
                    logger.error("Only .py files are supported")
                    continue

                logger.info(f"Storing file: {file_path}")
                from instructorchat.retrieval.store import store_documents

                success, message = store_documents(file_path)
                if success:
                    logger.info(message)
                else:
                    logger.error(message)
            except Exception:
                logger.error(traceback.format_exc())
            continue

        if not inp:
            print("exit...")
            break

        # Get relevant context for the query
        contexts = await retrieve_relevant_context(inp, api_key, folder=folder)

        # Prepare the prompt with context
        # context_text = "\n\n".join([
        #     f"Title: {ctx['title']}\n{ctx['text']}"
        #     for ctx in contexts
        # ])

        # Format the message with context and question
        # formatted_message = f"""
        #     Here is the question: <QUESTION> {inp} </QUESTION>

        #     The following are the contexts:
        #     <CONTEXT>
        #     {context_text}
        #     </CONTEXT>"""

        message = Message("user").add_text(f"Here is the question: <question>{inp}</question>\n\nThe following are contexts:\n")
        images = dict()

        for i, context in enumerate(contexts):
            message.add_text("<context>\n")

            message.add_text(f"Title: {context["title"]}\n")

            if context["image_dir"] is not None and context["image_dir"] not in images:
                images[context["image_dir"]] = i  # Mark this context as containing an image

                message.add_image(Image.open(context["image_dir"]))
                message.add_text("\nText parsed from image:\n")

            message.add_text(f"{context["text"]}\n</context>\n")

        # Add messages to conversation
        conv.append_message(message)

        # Create the final prompt with context
        messages = conv.to_openai_api_messages()

        gen_params = {
            "messages": messages,
            "temperature": temperature
        }

        stream = await generate_response_stream(gen_params)

        if stream is not None:
            response = await chatio.stream_output(stream)
            # Add response to complete a question-response pair

            conv.append_message(Message("assistant").add_text(response.strip()))

            if evaluation_test_cases:
                yield {
                    "idx": idx,
                    "input": inp,
                    "actual_output": response,
                    "retrieval_context": [{
                        "title": ctx["title"],
                        "text": ctx["text"],
                        "image_dir": ctx["image_dir"] if i in images.values() else None
                    } for i, ctx in enumerate(contexts)],
                    "expected_output": evaluation_test_cases[idx]["expected_output"],
                    "context": evaluation_test_cases[idx]["context"] if "context" in evaluation_test_cases[idx] else None,
                }

                idx += 1

                conv = adapter.get_default_conv_template(model_path)  # Reset conversation

                if idx >= len(evaluation_test_cases):
                    break
        else:
            logger.error("Received empty stream")
