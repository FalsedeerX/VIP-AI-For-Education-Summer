import base64
from enum import IntEnum, auto
from io import BytesIO
from typing import List, Tuple, Union, Dict, TypeAlias
import json
from PIL import Image

class SeparatorStyle(IntEnum):
    """Separator styles."""
    DEFAULT = auto()
    GPT = auto()

class ContentType(IntEnum):
    TEXT = auto()
    IMAGE = auto()

MessageType: TypeAlias = Union[str, List[Tuple[ContentType, Union[str, Image.Image]]]]
OpenAIContentListType: TypeAlias = List[Dict[str, Union[str, Dict[str, str]]]]

def encode_image(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

class Conversation:
    """A class that manages conversation history."""

    def __init__(self):
        self.name = "gpt4_mini"
        self.system_message = "You are a helpful AI assistant." #change prompt for instructor AI
        self.roles = ("user", "assistant")
        # this variable goes into the database
        # might need to consider having multimodel's url with the text | Each message is either a string or a tuple of (string, List[image_url]).
        self.messages: List[Tuple[str, MessageType]] = []
        self.offset = 0 #zero-shot
        self.sep_style = SeparatorStyle.GPT
        self.sep = "\n"
        self.stop_str = None

    # def get_prompt(self) -> str:
    #     """Get the prompt for generation."""
    #     return self.messages[-1][1] if self.messages else ""

    def set_system_message(self, system_message: str):
        """Set the system message."""
        self.system_message = system_message

    def append_message(self, role: str, message: MessageType):
        """Append a new message."""
        self.messages.append((role, message))

    # def update_last_message(self, message: str):
    #     """Update the last message."""
    #     if self.messages:
    #         self.messages[-1][1] = message

    def to_openai_api_messages(self):
        """Convert the conversation to OpenAI API format."""
        messages: List[Dict[str, Union[str, OpenAIContentListType]]] = [{"role": "system", "content": self.system_message}]
        for role, message in self.messages:
            if isinstance(message, str):
                messages.append({"role": role, "content": message})
            else:
                if isinstance(message, str):
                    messages.append({"role": role, "content": message})
                else:
                    content_items: OpenAIContentListType = []
                    for content_type, item in message:
                        if content_type == ContentType.TEXT:
                            assert isinstance(item, str), f"Received {content_type, item} but 'ContentType.TEXT' must be paired with a string."
                            content_items.append({"text": item})
                        else:
                            if isinstance(item, str):
                                content_items.append({"image_url": {"url": item}})
                            else:
                                content_items.append({"image_url": {"url": encode_image(item)}})

                    messages.append({"role": role, "content": content_items})
        return messages

    def get_message(self):
        return self.messages

    def save_conversation(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump(self.messages, f, indent=4)

def get_conv_template(name: str) -> Conversation:
    """Get a new conversation template."""
    return Conversation()