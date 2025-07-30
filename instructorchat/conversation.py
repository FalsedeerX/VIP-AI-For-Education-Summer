from enum import IntEnum, auto
from typing import List, Tuple, Literal
from PIL import Image
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionContentPartParam
import math
import tiktoken
import openai
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY") 

GPT4O_MINI_MAX_TOKENS = 128000
ENCODING_NAME = "gpt-4o"
MAX_TOKEN_RATIO = 0.7

def count_tokens_tiktoken(text: str, encoding_name: str = ENCODING_NAME) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(text))

from instructorchat.utils import image_to_base64


Role = Literal["user", "assistant"]


class ContentType(IntEnum):
    TEXT = auto()
    IMAGE = auto()


class Message:
    def __init__(self, role: Role) -> None:
        self.role: Role = role
        self.content: List[Tuple[ContentType, str]] = []

    def add_text(self, text: str) -> 'Message':
        self.content.append((ContentType.TEXT, text))
        return self

    def add_image(self, image: Image.Image) -> 'Message':
        self.content.append((ContentType.IMAGE, image_to_base64(image)))
        return self

    def to_openai_message(self) -> ChatCompletionMessageParam:
        openai_content: List[ChatCompletionContentPartParam] = []

        for content_part in self.content:
            if content_part[0] == ContentType.TEXT:
                openai_content.append({
                    "type": "text",
                    "text": content_part[1]
                })
            else:
                openai_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{content_part[1]}"}
                })

        return {
            "role": self.role,  # type: ignore
            "content": openai_content
        }

    def __repr__(self) -> str:
        content_str = ""

        for content_type, content_value in self.content:
            if content_type == ContentType.TEXT:
                content_str += content_value
            elif content_type == ContentType.IMAGE:
                content_str += "[Image]"

        return f'Message(role={self.role}, content="{content_str})"'


class Conversation:
    """A class that manages conversation history."""

    def __init__(self):
        # self.name = "gpt4_mini"
        self.system_message = "You are a helpful AI assistant."
        self.messages: List[Message] = []
        self.title: Optional[str] = None

    def set_system_message(self, system_message: str):
        """Set the system message."""
        self.system_message = system_message

    def append_message(self, message: Message):
        """Append a new message."""
        self.messages.append(message)

    def to_openai_api_messages(self):
        """Convert the conversation to OpenAI API format."""
        messages: List[ChatCompletionMessageParam] = [{
            "role": "system",
            "content": self.system_message
        }]

        for message in self.messages:
            messages.append(message.to_openai_message())

        return messages

    async def generate_title(self, api_key: str) -> str:
        """Generate a concise conversation title based on the first Q&A pair."""
        if self.title:
            return self.title
        if len(self.messages) < 2:
            raise ValueError("Need at least one user message and one assistant message to generate a title.")
        # Extract text from first user and assistant messages
        user_text = "".join(content for ctype, content in self.messages[0].content if ctype == ContentType.TEXT)
        assistant_text = "".join(content for ctype, content in self.messages[1].content if ctype == ContentType.TEXT)
        prompt = (
            f"Create a concise title for this conversation session. "
            f"User asked: '{user_text}'. Assistant replied: '{assistant_text}'."
        )
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that crafts conversation titles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0.0
        )
        title_text = response.choices[0].message.content.strip().strip('"')
        self.title = title_text
        return self.title

    async def get_messages(self): 
        """
        Return the conversation messages, ensuring they are under the token threshold.
        If the token count exceeds the threshold, trim and summarize as needed.
        The OpenAI API key is taken from the argument or from the OPENAI_API_KEY environment variable.
        """
        max_tokens = int(GPT4O_MINI_MAX_TOKENS * MAX_TOKEN_RATIO)
        print(self.estimate_token_count())
        if self.estimate_token_count() > max_tokens:
            await self.trim_and_summarize_if_needed()
            print("trimmed")
            # Double-check after summarization
            if self.estimate_token_count() > max_tokens:
                raise ValueError("Conversation still exceeds token limit after summarization.")
        return self.messages

    def estimate_token_count(self):
        """Estimate the total token count of the conversation using tiktoken."""
        total_tokens = 0
        for msg in self.messages:
            for ctype, content in msg.content:
                total_tokens += count_tokens_tiktoken(content)
        return total_tokens

    async def summarize_messages_llm(self, messages):
        """Summarize a list of messages into a single message using gpt-4o-mini."""
        # Concatenate all text content
        conversation_text = "\n".join(
            content for msg in messages for ctype, content in msg.content if ctype == ContentType.TEXT
        )
        prompt = (
            "Summarize the following conversation history in a concise way, preserving important facts, context, and user intent. "
            "The summary should be clear and useful for continuing the conversation.\n\n"
            f"Conversation:\n{conversation_text}\n\nSummary:"
        )
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                {"role": "user", "content": prompt}
            ]
        )
        summary_text = response.choices[0].message.content.strip()
        summary_msg = Message(role="user")
        summary_msg.add_text(f"[Summary of earlier conversation]: {summary_text}")
        return summary_msg

    async def trim_and_summarize_if_needed(self):
        """If token count exceeds 0.7 * max, summarize earlier messages and keep only the most recent ones."""
        max_tokens = int(GPT4O_MINI_MAX_TOKENS * MAX_TOKEN_RATIO)
        if self.estimate_token_count() > max_tokens:
            # Keep the most recent messages that fit under the limit
            running_tokens = 0
            kept_messages = []
            # Iterate from the end (most recent)
            for msg in reversed(self.messages):
                msg_tokens = sum(count_tokens_tiktoken(content) for ctype, content in msg.content)
                if running_tokens + msg_tokens > max_tokens * 0.5:
                    break
                kept_messages.insert(0, msg)
                running_tokens += msg_tokens
            # Summarize the earlier messages
            num_to_summarize = len(self.messages) - len(kept_messages)
            if num_to_summarize > 0:
                summary_msg = await self.summarize_messages_llm(self.messages[:num_to_summarize])
                self.messages = [summary_msg] + kept_messages
            else:
                raise ValueError("Number of messages to summarize must be greater than 0. Check max_token_ratio")


def get_conv_template(name: str) -> Conversation:
    """Get a new conversation template."""
    return Conversation()


import time
if __name__ == "__main__":
    import asyncio


    # Simulate a conversation
    conv = Conversation()
    print(conv.get_messages())
    for i in range(1000):
        msg = Message(role="user" if i % 2 == 0 else "assistant")
        msg.add_text(f"This is message number {i}. " + ("Extra text. " * 50))
        conv.append_message(msg)

    async def test_conversation():
        messages = await conv.get_messages()
        print(f"Number of messages after summarization/trim: {len(messages)}")
        for idx, msg in enumerate(messages):
            print(f"Message {idx} (role={msg.role}):")
            for ctype, content in msg.content:
                print(f"  - {content[:100]}{'...' if len(content) > 100 else ''}")

    asyncio.run(test_conversation())
