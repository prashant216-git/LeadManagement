from fastapi import FastAPI

from app.api.whatsappwebhook import router as webhook_router
from app.db.database import Base, engine
from app.models.User import User
from app.models.messages import Message
from app.models.summary import Summary
from app.models.Ai_Draft import AIDraft
from app.api.AIWebhook import router as airouter
from app.api.UsersRoute import router as usersrouter
app = FastAPI()

app.include_router(webhook_router)
app.include_router(airouter)
app.include_router(usersrouter)

Base.metadata.create_all(bind=engine)
print("Creating tables...")