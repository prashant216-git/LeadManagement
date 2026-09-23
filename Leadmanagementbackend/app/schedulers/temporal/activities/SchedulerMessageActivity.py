from uuid import UUID

from temporalio import activity

from app.db.session import get_db
from app.dependencies.ObjectConstructor import build_channel_service
from app.enums.message import ScheduledMessageStatus
from app.models.scheduled_message import ScheduledMessage
from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.Scheduled_message_repository import ScheduledMessageRepository


@activity.defn
async def send_scheduled_message(
    scheduled_message_id: str,
):
    for db in get_db():

        try :
            scheduled_message_id=UUID(scheduled_message_id)
            channel_service= build_channel_service(db)
            scheduled_message_repo=ScheduledMessageRepository(db)
            scheduled_message=scheduled_message_repo.get_by_id(scheduled_message_id)
            channel_connection_repo=ChannelConnectionRepository(db)
            connection=channel_connection_repo.get_by_id(scheduled_message.channel_connection_id)


            result=await channel_service.send_message(lead_id=scheduled_message.lead_id,connection_id=scheduled_message.channel_connection_id,content=scheduled_message.content,channel_id=connection.channel_id,reply_to_message_id=None)
            if result:
                scheduled_message.status=ScheduledMessageStatus.SENT
                db.add(scheduled_message)
                db.commit()








        except Exception as e :
            print(e)
