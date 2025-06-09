"""Inference for GPT-4-mini model."""
import abc
import openai
from typing import Dict, Iterator, Optional

from instructorchat.retrieval.retrieval import Retrieval

class ChatIO(abc.ABC):
    @abc.abstractmethod
    async def prompt_for_input(self, role: str) -> str:
        """Prompt for input from a role."""

    @abc.abstractmethod
    async def prompt_for_output(self, role: str):
        """Prompt for output from a role."""

    @abc.abstractmethod
    async def stream_output(self, output_stream):
        """Stream output."""

async def generate_stream(params: Dict):
    """Generate response using OpenAI API."""
    try:
        client = openai.AsyncOpenAI(api_key=openai.api_key)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=params["messages"],
            temperature=0.7,
            stream=True,
        )
        return response

        #This code defines a generator function that streams the response from OpenAI’s ChatCompletion API (using gpt-4o-mini) as it is being generated, rather than waiting for the full answer.
        # collected_messages = []
        # for chunk in response:
        #     if chunk.choices[0].delta.content:
        #         content = chunk.choices[0].delta.content or ""
        #         collected_messages.append(content)
        #         yield {"text": "".join(collected_messages)}

    except Exception as e:
        print("hi,error roi nayy")
        return(f"Error: {str(e)}")
        #yield {"text": f"Error: {str(e)}"}

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

    from instructorchat.model.model_adapter import load_model, get_model_adapter
    from instructorchat.conversation import get_conv_template #if have more models => more templates => need for getting a correct templ

    # Load model
    adapter = get_model_adapter(model_path)
    load_model(model_path, api_key)
    conv = adapter.get_default_conv_template(model_path)

    retrieval = Retrieval()
    retrieval.populate_pipelines()

    while True:
        inp = await chatio.prompt_for_input(conv.roles[0])
    # list of commands
        if inp == "return conv":
            print(conv.get_message())
            continue

        if not inp:
            print("exit...")
            break

    # response generation

        conv.append_message(conv.roles[0], inp)
        #conv.append_message(conv.roles[1], None)

        contexts = retrieval.retrieve_documents(inp)
        messages = conv.to_openai_api_messages()
        content = retrieval.create_prompt_with_retrievals(inp, " ".join(contexts["contents"]))
        messages.append({"role": "user", "content": content})

        gen_params = {
            "messages": messages,
            "temperature": temperature,
        }

        await chatio.prompt_for_output(conv.roles[1])
        output_stream = await generate_stream(gen_params)
        outputs = await chatio.stream_output(output_stream)
        conv.update_last_message(outputs.strip())
        #print(conv.get_message)
