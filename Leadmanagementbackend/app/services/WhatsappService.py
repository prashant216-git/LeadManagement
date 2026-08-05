import os
import requests

from dotenv import load_dotenv

load_dotenv()


class WhatsAppService:

    @staticmethod
    def send_text_message(
        phone_number: str,
        message: str
    ):
        print("trying sending message to"+phone_number)

        url = (
            f"https://graph.facebook.com/v25.0/"
            f"{os.getenv('PHONE_NUMBER_ID')}/messages"
        )



        headers = {
            "Authorization":
                f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
            "Content-Type":
                "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )


        print(response.status_code)
        print(response.text)

        response.raise_for_status()
        return response.json()