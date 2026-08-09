from fastapi import FastAPI
import app.channel_engine.providers
from starlette.middleware.cors import CORSMiddleware
from app.api.channel_controller import router as channel_router
from app.api.whatsappwebhook import router as webhook_router
from app.db.database import Base, engine
from app.models.Leads import Lead
from app.models.messages import Message
from app.models.summary import Summary
from app.models.Ai_Draft import AIDraft
from app.api.AIWebhook import router as airouter
from app.api.UsersRoute import router as usersrouter
from app.core.config import settings
from app.api.channel_webhook_controller import router as webhook_controller


from app.api.AIREPLYHOOK import router as replyrouter
app = FastAPI()
origins = [
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
    "https://veloratechnologies.in",
    "https://api.veloratechnologies.in",
    "https://www.veloratechnologies.in",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(airouter)
app.include_router(usersrouter)
app.include_router(webhook_controller)
app.include_router(replyrouter)


app.include_router(channel_router)

Base.metadata.create_all(bind=engine)
print("Creating tables...")