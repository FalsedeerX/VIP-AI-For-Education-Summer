"""Model adapter for GPT-4-mini."""
import os
from typing import Optional
import openai
from instructorchat.conversation import Conversation, get_conv_template

class BaseModelAdapter:
    """Base model adapter."""

    def match(self, model_path: str):
        return True

    def load_model(self, model_path: str, api_key: Optional[str] = None):
        if api_key:
            openai.api_key = api_key
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            raise ValueError("OpenAI API key must be provided")
        return None, None  # No actual model/tokenizer needed for API calls

    def get_default_conv_template(self, model_path: str) -> Conversation:
        return get_conv_template("gpt4_mini")

class GPT4MiniAdapter(BaseModelAdapter):
    """The model adapter for GPT-4-mini"""

    def match(self, model_path: str):
        return "gpt-4o-mini" in model_path.lower()

    def load_model(self, model_path: str, api_key: Optional[str] = None):
        if api_key:
            openai.api_key = api_key
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            raise ValueError("OpenAI API key must be provided")
        return None, None  # No actual model/tokenizer needed for API calls

    def get_default_conv_template(self, model_path: str) -> Conversation:
        return get_conv_template("gpt4_mini")

def get_model_adapter(model_path: str) -> BaseModelAdapter:
    """Get a model adapter for the model_path."""
    adapter = GPT4MiniAdapter()
    if adapter.match(model_path):
        return adapter
    return BaseModelAdapter()

def load_model(model_path: str, api_key: Optional[str] = None):
    """Load a model and its tokenizer."""
    adapter = get_model_adapter(model_path)
    return adapter.load_model(model_path, api_key)