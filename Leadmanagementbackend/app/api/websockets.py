from uuid import UUID

from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect

from app.socketmanager.websocketmanager import websocketmanager

router = APIRouter(
    prefix="/weboscket",
    tags=["websockets"],
)
manager= websocketmanager()
@router.websocket("/ws/leads_message/{lead_id}")

async def lead_message_websocket(websocket:WebSocket,
                                 lead_id:UUID):
    print(f"entered for lead lead_id: {lead_id}")
    lead_id=str(lead_id)
    await manager.connect(lead_id=lead_id,websocket=websocket)

    try:
        while True:
            data =await websocket.receive_json()
            print(f"data for {lead_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(lead_id=lead_id,websocket=websocket)


