from uuid import UUID

from temporalio import activity

from app.db.session import get_db
from app.dependencies.ObjectConstructor import build_channel_service
from app.enums.message import ScheduledMessageStatus

from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.Scheduled_message_repository import ScheduledMessageRepository

from app.repositories.AttachementRepository import AttachmentRepository


@activity.defn
async def send_scheduled_message(
    scheduled_message_id: str,
):
    for db in get_db():

        try :
            scheduled_message_id=UUID(scheduled_message_id)
            channel_service= build_channel_service(db)

            attachment_repository=AttachmentRepository(db)

            scheduled_message_repo=ScheduledMessageRepository(db)
            scheduled_message=scheduled_message_repo.get_by_id(scheduled_message_id)
            channel_connection_repo=ChannelConnectionRepository(db)
            connection=channel_connection_repo.get_by_id(scheduled_message.channel_connection_id)

            scheduled_attachments = attachment_repository.get_by_message(
                scheduled_message.id
            )

            attachment_ids = [
                attachment.id
                for attachment in scheduled_attachments
            ]



            result=await channel_service.send_message(lead_id=scheduled_message.lead_id,connection_id=scheduled_message.channel_connection_id,content=scheduled_message.content,reply_to_message_id=None,attachment_ids=attachment_ids)
            if result:
                scheduled_message.status=ScheduledMessageStatus.SENT
                db.add(scheduled_message)
                db.commit()








        except Exception as e :
            print(e)
