# app/activities/channel_watch_activity.py

from datetime import datetime, timedelta, timezone

from temporalio import activity

from app.db.session import get_db
from app.dependencies.services import get_websocket_manager

from app.repositories.ChannelWatchRepository import (
    ChannelWatchRepository,
)
from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.ChannelCredentialRepository import (
    ChannelCredentialRepository,
)
from app.repositories.ChannelMasterRepositories import (
    ChannelMasterRepository,
)
from app.repositories.LeadRepository import LeadRepository
from app.repositories.LeadStatusMasterRepository import LeadStatusMasterRepository
from app.repositories.LeadStatusRepository import LeadStatusRepository
from app.repositories.MessageRepository import MessageRepository
from app.services.Leadmanagementservice import LeadService

from app.services.messageservice import MessageService
from app.channel_engine.channelresolver import ChannelResolver

from app.services.CredentialEncryptionService import (
    CredentialEncryptionService,
)

from app.channel_engine.engine import ChannelEngine
from app.socketmanager.websocketmanager import websocketmanager
from dependencies.ObjectConstructor import build_channel_service


@activity.defn
async def renew_expiring_channel_watches() -> dict:
    """
    Renew channel watches that will expire within the next 24 hours.
    """

    renewed_count = 0
    failed_count = 0

    # Renew watches expiring within the next 24 hours.
    expiry_limit = (
        datetime.now(timezone.utc)
        + timedelta(days=1)
    )

    for db in get_db():

        # --------------------------------------------------
        # Create repositories
        # --------------------------------------------------

        channel_watch_repository = ChannelWatchRepository(db)

        channel_service = build_channel_service(db)

        # --------------------------------------------------
        # Get expiring watches
        # --------------------------------------------------

        expiring_watches = (
            channel_watch_repository
            .get_watches_expiring_before(expiry_limit)
        )



        # --------------------------------------------------
        # Renew each watch
        # --------------------------------------------------

        for (
            watch,
            connection_id,
            provider_identifier,
            channel_id,
        ) in expiring_watches:

            try:
                activity.logger.info(
                    "Processing expiring channel watch",
                    extra={
                        "watch_id": watch.id,
                        "connection_id": connection_id,
                        "provider_identifier": (
                            provider_identifier
                        ),
                        "channel_id": channel_id,
                    },
                )

                return await channel_service.setup_watch(identifier=provider_identifier,
                                                          channel_code="gmail"
                                                         )

                # --------------------------------------------------
                # Gmail provider
                # --------------------------------------------------




                # --------------------------------------------------
                # Unsupported provider
                # --------------------------------------------------


                # --------------------------------------------------
                # Update watch after successful renewal
                # --------------------------------------------------



                renewed_count += 1

                activity.logger.info(
                    "Channel watch renewed successfully",
                    extra={
                        "watch_id": watch.id,
                        "connection_id": connection_id,
                        "provider_identifier": (
                            provider_identifier
                        ),
                    },
                )

            except Exception as exc:
                failed_count += 1

                db.rollback()

                activity.logger.exception(
                    "Failed to renew channel watch",
                    extra={
                        "watch_id": watch.id,
                        "connection_id": connection_id,
                        "provider_identifier": (
                            provider_identifier
                        ),
                        "error": str(exc),
                    },
                )
                raise

        break

    return {
        "renewed_count": renewed_count,
        "failed_count": failed_count,
    }