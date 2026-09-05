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
        print(f"after connect")
        print(self.connections)

    def disconnect(self,lead_id:str,websocket:WebSocket):
        if lead_id not in self.connections:
            return
        if websocket in self.connections[lead_id]:
            self.connections[lead_id].remove(websocket)

        if not self.connections[lead_id]:
            del self.connections[lead_id]
        print("AFTER DISCONNECT:")

    async def send_to_lead(self,lead_id:str , data:MessageDetailsDTO):
        print("entered .......... sedningwebsocet")

        print(self.connections)
        lead_id=str(lead_id)

        connectionsthislead = self.connections[lead_id]
        print(connectionsthislead)
        disconnected=[]
        for websocket in connectionsthislead:
            try :
                print("datais"+data)
                await websocket.send_json(data.model_dump(mode="json"))
            except Exception as e:
                print(e)

                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(lead_id,websocket)



