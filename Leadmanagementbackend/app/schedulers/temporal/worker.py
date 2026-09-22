# app/schedulers/temporal/worker.py

import asyncio

from temporalio.worker import Worker

from app.core.config import settings
from app.schedulers.temporal.activities.SchedulerMessageActivity import send_scheduled_message
from app.schedulers.temporal.client import get_temporal_client
from app.schedulers.temporal.workflows.SchedulerMessageWorkflow import (
    ScheduledMessageWorkflow,
)

from app.schedulers.temporal.workflows.gmail_watch_renewal_workflow import (
    GmailWatchRenewalWorkflow,
)

from app.schedulers.temporal.activities.gmail_watch_renewal_activity import (
    renew_expiring_channel_watches,
)
from app.channel_engine.providers.gmail_provider import (
    GmailProvider,
)


async def create_temporal_worker():
    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
        workflows=[
            GmailWatchRenewalWorkflow,
            ScheduledMessageWorkflow,
        ],
        activities=[
            renew_expiring_channel_watches,
            send_scheduled_message,
        ],
    )

    return client, worker


async def main():
    client, worker = await create_temporal_worker()

    print(
        "Temporal worker started on task queue:",
        settings.TEMPORAL_TASK_QUEUE,
    )

    try:
        await worker.run()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())