from typing import List, Optional
import sys
import os
import logging

from state_store.get_redis_user_state import get_redis_user_state

from ..ai_constants import DEFAULT_SYSTEM_CONTENT
from .anthropic import AnthropicAPI
from .openai import OpenAI_API
from .vertexai import VertexAPI
from .genai import GenAI_API

"""
New AI providers must be added below.
`get_available_providers()`
This function retrieves available API models from different AI providers.
It combines the available models into a single dictionary.
`_get_provider()`
This function returns an instance of the appropriate API provider based on the given provider name.
`get_provider_response`()
This function retrieves the user's selected API provider and model,
sets the model, and generates a response.
Note that context is an optional parameter because some functionalities,
such as commands, do not allow access to conversation history if the bot
isn't in the channel where the command is run.
"""

# Set up logging
logger = logging.getLogger(__name__)


def get_available_providers():
    return {
        **AnthropicAPI().get_models(),
        **OpenAI_API().get_models(),
        **VertexAPI().get_models(),
        **GenAI_API().get_models(),
    }


def _get_provider(provider_name: str):
    if provider_name.lower() == "anthropic":
        return AnthropicAPI()
    elif provider_name.lower() == "openai":
        return OpenAI_API()
    elif provider_name.lower() == "vertexai":
        return VertexAPI()
    elif provider_name.lower() == "genai":
        return GenAI_API()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def _estimate_token_count(text: str) -> int:
    """Roughly estimate token count based on words (very approximate)"""
    # A very rough approximation: 1 token ≈ 0.75 words
    return int(len(text.split()) / 0.75)


def get_provider_response(user_id: str, prompt: str, context: Optional[List] = [], system_content=DEFAULT_SYSTEM_CONTENT):
    formatted_context = "\n".join([f"{msg['user']}: {msg['text']}" for msg in context])
    full_prompt = f"Prompt: {prompt}\nContext: {formatted_context}"
    context_token_count = _estimate_token_count(full_prompt)
    print(f"🤖 Getting AI response for user: {user_id}")
    
    try:
        provider_name = None
        model_name = None
        
        # Check if Redis is available
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            try:
                # Try to get user's model selection from Redis
                provider_name, model_name = get_redis_user_state(user_id, False, redis_url)
            except Exception as e:
                print(f"⚠️ Failed to get user state from Redis: {e}")
                # Fall through to GenAI fallback
        
        # Fall back to GenAI if no provider/model or Redis is not available
        if not provider_name or not model_name:
            print(f"ℹ️ No provider/model selection found for user: {user_id}, falling back to GenAI")
            provider_name = "genai"
            model_name = "genai-agent"
        
        print(f"🔧 Using provider: {provider_name}, model: {model_name}")
        provider = _get_provider(provider_name)
        provider.set_model(model_name)
        
        print(f"📝 Generating response with {len(context)} context messages (approx. {context_token_count} tokens)")
        response = provider.generate_response(full_prompt, system_content)
        
        response_token_count = _estimate_token_count(response)
        print(f"✅ Successfully generated response for user: {user_id} (approx. {response_token_count} tokens)")
        return response
    except Exception as e:
        error_msg = f"❌ Error generating AI response: {e}"
        print(error_msg, file=sys.stderr)
        raise e
