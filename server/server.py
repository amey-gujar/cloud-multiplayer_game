import asyncio
import json
import os
import time

import websockets
from game_room import GameRoom


room = GameRoom(room_id="room_1")
connected_clients = {}


async def game_tick_loop():
    previous_time = time.time()
    while True:
        current_time = time.time()
        dt = current_time - previous_time
        previous_time = current_time

        room.update(dt, current_time)
        if connected_clients:
            snapshot = room.get_snapshot()
            message = json.dumps(snapshot)
            await asyncio.gather(
                *(websocket.send(message) for websocket in list(connected_clients))
            )

        await asyncio.sleep(0.05)


async def handler(websocket):
    player_id = None
    try:
        try:
            join_message = await websocket.recv()
            data = json.loads(join_message)
            if data.get("type") == "join":
                player_id = data.get("id")
                username = data.get("username")
            else:
                username = None
        except (json.JSONDecodeError, TypeError):
            username = None

        if not player_id or not username:
            player_id = f"player_{id(websocket)}"
            username = "Player"

        room.add_player(player_id, username)
        connected_clients[websocket] = player_id
        await websocket.send(json.dumps({"type": "joined", "player_id": player_id}))

        async for message in websocket:
            try:
                data = json.loads(message)
            except (json.JSONDecodeError, TypeError):
                continue

            if data.get("type") == "input":
                room.handle_player_input(player_id, data, time.time())
            elif data.get("type") == "ping":
                pass
    except Exception as e:
        print(f"CRITICAL SERVER ERROR: {e}")
        raise e
    finally:
        if websocket in connected_clients:
            del connected_clients[websocket]
            room.remove_player(player_id)


async def main():
    port = int(os.environ.get("PORT", 8765))
    server = await websockets.serve(handler, "0.0.0.0", port)
    await asyncio.gather(server.wait_closed(), game_tick_loop())


if __name__ == "__main__":
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(main())
    else:
        asyncio.create_task(main())