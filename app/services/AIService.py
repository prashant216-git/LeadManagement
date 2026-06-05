import os

from openai import OpenAI

from app.services.Summaryservice import SummaryService
from app.services.messageservice import MessageService
from app.services.AIDraftService import AIDraftService

from dotenv import load_dotenv

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
            "summary": summary,
            "conversation": "\n".join(conversation)
        }

    @staticmethod
    def generate_reply(
            db,
            user_id: int,
            message_id: int
    ):
        context = AIService.build_context(
            db=db,
            user_id=user_id
        )
        prompt = f"""
        Conversation Summary:

        {context['summary']}

        Recent Messages:

        {context['conversation']}

        Generate a helpful reply.

        Only return the reply text.
        """


        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are a helpful customer Lead management assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )
        draft = (
            AIDraftService.create_draft(
                db=db,
                user_id=user_id,
                message_id=message_id,
                draft_text=response.choices[0].message.content
            )
        )
        print(response.choices[0].message.content)


