from datetime import datetime, timedelta, timezone

from app.channel_engine.engine import ChannelEngine
from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.ChannelWatchRepository import (
    ChannelWatchRepository,
)


class GmailWatchScheduler:

    def __init__(
        self,
        channel_connection_repository: ChannelConnectionRepository,
        channel_watch_repository: ChannelWatchRepository,
            channel_engine: ChannelEngine,
    ):
        self.channel_connection_repository = (
            channel_connection_repository
        )
        self.channel_watch_repository = (
            channel_watch_repository
        )
        self.channel_engine: ChannelEngine = channel_engine



    async def renew_expiring_watches(self):

        provider = self.channel_engine.create_provider(channel_code="gmail")

        now = datetime.now(timezone.utc)

        expiry_limit = now + timedelta(days=1)

        watches = (
            self.channel_watch_repository
            .get_watches_expiring_before(
                expiry_limit
            )
        )

        for watch in watches:

            connection = watch.channel_connection



            await provider.setup_watch(
                identifier=connection.probider_identifier,
                channel_id=connection.channel_id,
            )