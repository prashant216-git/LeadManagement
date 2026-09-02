from openai import OpenAI

from app.ai.providers.base_provider import BaseAIProvider
from app.core.config import settings


class DeepSeekProvider(BaseAIProvider):

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )

    def generate(
        self,
        system_prompt: str,

    ) -> str:

        print(system_prompt)

        response = self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },

            ],
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()