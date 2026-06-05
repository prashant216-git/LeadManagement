from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config.settings import VERIFY_TOKEN
from app.db.session import get_db
from app.services.messageservice import MessageService
from app.services.userservice import UserService

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
        hub_mode: str = None,
        hub_verify_token: str = None,
        hub_challenge: str = None
):
    if hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)

    return PlainTextResponse(
        content="Verification Failed",
        status_code=403
    )


@router.post("/webhook")
async def receive_message(
        request: Request,
        db: Session = Depends(get_db)
):
    try:

        body = await request.json()

        value = (
            body["entry"][0]
            ["changes"][0]
            ["value"]
        )

        messages = value.get("messages")

        if not messages:
            return {
                "status": "ignored"
            }

        contact = value["contacts"][0]
        message = messages[0]

        name = (
            contact
            .get("profile", {})
            .get("name")
        )

        phone_number = contact["wa_id"]

        channel_message_id = message["id"]

        message_type = message["type"]

        message_timestamp = int(
            message["timestamp"]
        )

        content = ""

        if message_type == "text":
            content = (
                message
                .get("text", {})
                .get("body", "")
            )

        existing_message = (
            MessageService
            .get_message_by_channel_message_id(
                db=db,
                channel_message_id=channel_message_id
            )
        )

        if existing_message:
            return {
                "status": "duplicate"
            }

        user = UserService.get_or_create_user(
            db=db,
            phone_number=phone_number,
            name=name
        )

        saved_message = (
            MessageService.save_message(
                db=db,
                user_id=user.id,
                channel="whatsapp",
                channel_message_id=channel_message_id,
                sender="user",
                message_type=message_type,
                content=content,
                message_timestamp=message_timestamp
            )
        )

        print("\n" + "=" * 60)
        print("NEW MESSAGE RECEIVED")
        print("=" * 60)
        print(f"User ID: {user.id}")
        print(f"Name: {name}")
        print(f"Phone: {phone_number}")
        print(f"Type: {message_type}")
        print(f"Content: {content}")
        print("=" * 60)

        return {
            "status": "success",
            "message_id": saved_message.id,
            "user_id": user.id
        }

    except Exception as e:

        print(
            f"WEBHOOK ERROR: {str(e)}"
        )

        return {
            "status": "error",
            "message": str(e)
        }