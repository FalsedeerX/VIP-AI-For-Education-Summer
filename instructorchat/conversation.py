from enum import IntEnum, auto
from typing import List, Tuple, Literal
from PIL import Image
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionContentPartParam

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

    def get_messages(self):
        return self.messages


def get_conv_template(name: str) -> Conversation:
    """Get a new conversation template."""
    return Conversation()
