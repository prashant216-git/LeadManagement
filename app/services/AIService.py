import os

from openai import OpenAI

from dotenv import load_dotenv

from app.services.Summaryservice import SummaryService
from app.services.messageservice import MessageService

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_KEY"),
    base_url=os.getenv("BASE_URL")
)


class AIService:

    @staticmethod
    def build_context(
        db,
        user_id: int
    ):

        summary = SummaryService.get_summary_text(
            db=db,
            user_id=user_id
        )

        messages = MessageService.get_recent_messages(
            db=db,
            user_id=user_id,
            limit=5
        )

        conversation = []

        for message in messages:

            conversation.append(
                f"{message.sender}: {message.content}"
            )

        return {
            "summary": summary or "",
            "conversation": "\n".join(conversation)
        }

    @staticmethod
    def generate_reply(
        db,
        user_id: int
    ) -> str:

        context = AIService.build_context(
            db=db,
            user_id=user_id
        )

        prompt = f"""
Conversation Summary:

{context["summary"]}

Recent Messages:

{context["conversation"]}

Generate a helpful customer support reply.

Only return the reply text.
"""

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are a helpful customer lead management assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    @staticmethod
    def generate_initial_summary(
            messages
    ) -> str:

        conversation = []

        for message in messages:
            conversation.append(
                f"{message.sender}: {message.content}"
            )

        prompt = f"""
    Summarize the following customer conversation.

    Focus on:
    - Customer requirements
    - Important facts
    - Pending actions
    - Decisions taken

    Conversation:

    {chr(10).join(conversation)}

    Return only the summary.
    """

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content":
                        "You create concise conversation summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    @staticmethod
    def update_summary(
            existing_summary: str,
            messages
    ) -> str:

        conversation = []

        for message in messages:
            conversation.append(
                f"{message.sender}: {message.content}"
            )

        prompt = f"""
    Existing Summary:

    {existing_summary}

    New Messages:

    {chr(10).join(conversation)}

    Update the summary using the new messages.

    Return only the updated summary.
    """

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content":
                        "You maintain conversation summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()