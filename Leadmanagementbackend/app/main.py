from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import app.channel_engine.providers

from app.api.Aicontroller import router as ai_controller
from app.api.channel_controller import router as channel_router
from app.api.channel_webhook_controller import router as webhook_controller
from app.api.dashboard_controller import router as dashboard_controller
from app.api.Leadscontroller import router as lead_controller
from app.api.meeting_router import router as meeting_router
from app.api.websockets import router as websocket_router

from app.db.database import Base, engine
from app.schedulers.temporal.startup_scheduler import register_static_schedulers
from app.schedulers.temporal.worker import create_temporal_worker
from app.api.Schedules import router as schedules_router
from app.api.Lead_Status_Controller import router as lead_status_controller


@asynccontextmanager
async def lifespan(app: FastAPI):

    temporal_client, temporal_worker = (
        await create_temporal_worker()
    )

    await register_static_schedulers(
        temporal_client
    )

    print("Temporal schedules registered.")

    try:
        yield

    finally:
        await temporal_worker.shutdown()
        await temporal_client.close()


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://veloratechnologies.in",
    "https://api.veloratechnologies.in",
    "https://www.veloratechnologies.in",
    "https://crm.veloratechnologies.in",
    "https://api-ai.silexatechnologies.com",
    "https://crm.silexatechnologies.com",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(webhook_controller)
app.include_router(websocket_router)
app.include_router(meeting_router)
app.include_router(dashboard_controller)
app.include_router(lead_controller)
app.include_router(channel_router)
app.include_router(ai_controller)
app.include_router(lead_status_controller)
app.include_router(schedules_router)



Base.metadata.create_all(bind=engine)

print("Creating tables...")