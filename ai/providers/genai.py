import openai
from .base_provider import BaseAPIProvider
import os
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class GenAI_API(BaseAPIProvider):
    MODELS = {
        "droplet-agent": {"name": "Droplet Agent", "provider": "GenAI", "max_tokens": 4096},
        "claude-3-sonnet-20240229": {"name": "Claude 3 Sonnet", "provider": "GenAI", "max_tokens": 4096},
        "claude-3-haiku-20240307": {"name": "Claude 3 Haiku", "provider": "GenAI", "max_tokens": 4096},
        "gpt-4-turbo": {"name": "GPT-4 Turbo", "provider": "GenAI", "max_tokens": 4096},
        "gpt-4o": {"name": "GPT-4o", "provider": "GenAI", "max_tokens": 4096},
    }

    def __init__(self):
        self.api_key = os.environ.get("GENAI_API_KEY")
        self.base_url = os.environ.get("GENAI_API_URL", "https://api.genai.example.com/v1")

    def set_model(self, model_name: str):
        if model_name not in self.MODELS.keys():
            raise ValueError("Invalid model")
        self.current_model = model_name

    def get_models(self) -> dict:
        if self.api_key is not None:
            return self.MODELS
        else:
            return {}

    def generate_response(self, prompt: str, system_content: str) -> str:
        try:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            response = self.client.chat.completions.create(
                model=self.current_model,
                n=1,
                messages=[{"role": "system", "content": system_content}, {"role": "user", "content": prompt}],
                max_tokens=self.MODELS[self.current_model]["max_tokens"],
            )
            return response.choices[0].message.content
        except openai.APIConnectionError as e:
            logger.error(f"Server could not be reached: {e.__cause__}")
            raise e
        except openai.RateLimitError as e:
            logger.error(f"A 429 status code was received. {e}")
            raise e
        except openai.AuthenticationError as e:
            logger.error(f"There's an issue with your API key. {e}")
            raise e
        except openai.APIStatusError as e:
            logger.error(f"Another non-200-range status code was received: {e.status_code}")
            raise e 