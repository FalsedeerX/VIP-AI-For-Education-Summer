from enum import IntEnum, auto
from typing import List, Tuple, Union

class SeparatorStyle(IntEnum):
    """Separator styles."""
    DEFAULT = auto()
    GPT = auto()

class Conversation:
    """A class that manages conversation history."""
    
    def __init__(self):
        self.name = "gpt4_mini"
        self.system_message = "You are a helpful AI assistant." #change prompt for instructor AI
        self.roles = ("user", "assistant")
        # this variable goes into the database
        # might need to consider having multimodel's url with the text | Each message is either a string or a tuple of (string, List[image_url]).
        self.messages = [] 
        self.offset = 0 #zero-shot
        self.sep_style = SeparatorStyle.GPT
        self.sep = "\n"
        self.stop_str = None

    def get_prompt(self) -> str:
        """Get the prompt for generation."""
        return self.messages[-1][1] if self.messages else ""

    def set_system_message(self, system_message: str):
        """Set the system message."""
        self.system_message = system_message

    def append_message(self, role: str, message: str):
        """Append a new message."""
        self.messages.append([role, message])

    def update_last_message(self, message: str):
        """Update the last message."""
        if self.messages:
            self.messages[-1][1] = message

    def to_openai_api_messages(self):
        """Convert the conversation to OpenAI API format."""
        messages = [{"role": "system", "content": self.system_message}]
        for role, message in self.messages:
            messages.append({"role": role, "content": message})
        return messages
    
    def get_message(self):
        return self.messages

def get_conv_template(name: str) -> Conversation:
    """Get a new conversation template."""
    return Conversation() 