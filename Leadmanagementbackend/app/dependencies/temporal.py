from fastapi import Depends
from temporalio.client import Client

from app.schedulers.temporal.client import get_temporal_client
from app.schedulers.temporal.scheduler_dynamic import TemporalScheduler


def get_temporal_scheduler(
    client: Client = Depends(get_temporal_client),
) -> TemporalScheduler:

    return TemporalScheduler(
        client=client,
    )