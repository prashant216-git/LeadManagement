from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import WebSocket, WebSocketDisconnect

from app.socketmanager.websocketmanager import websocketmanager
from app.dependencies.services import get_websocket_manager

router = APIRouter(
    prefix="/websocket",
    tags=["websockets"],
)

@router.websocket("/ws/leads_message/{lead_id}")

async def lead_message_websocket(websocket:WebSocket,
                                 lead_id:UUID,manager :websocketmanager =Depends(get_websocket_manager)):
    print(f"entered for lead lead_id: {lead_id}")
    lead_id=str(lead_id)
    print("WS before connect MANAGER:", id(manager))
    await manager.connect(lead_id=lead_id,websocket=websocket)
    print("WS after connect MANAGER:", id(manager))

    try:
        while True:
            data =await websocket.receive_json()
            print(f"data for {lead_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(lead_id=lead_id,websocket=websocket)


