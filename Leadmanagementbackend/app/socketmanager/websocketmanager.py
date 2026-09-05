from collections import defaultdict

from fastapi import WebSocket

from app.DTOs.MessageDTO import MessageDetailsDTO


class websocketmanager:
    def __init__(self):
        self.connections:dict[str,list[WebSocket]] =defaultdict(list)

    async def connect(
            self,
    lead_id:str,
    websocket:WebSocket,
    ):
        print(f"connecting to lead lead_id: {lead_id}")
        await websocket.accept()
        self.connections[lead_id].append(websocket)

    def disconnect(self,lead_id:str,websocket:WebSocket):
        if lead_id not in self.connections:
            return
        if websocket in self.connections[lead_id]:
            self.connections[lead_id].remove(websocket)
        if not self.connections[lead_id]:
            del self.connections[lead_id]

    async def send_to_lead(self,lead_id:str , data:MessageDetailsDTO):
        connections = self.connections[lead_id]
        disconnected=[]
        for websocket in connections:
            try :
                await websocket.send_json(data)
            except Exception as e:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(lead_id,websocket)



