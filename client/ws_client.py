import asyncio
import json
import queue
import threading

import websockets


send_queue = queue.Queue()
receive_queue = queue.Queue()
connected = False


async def _network_loop(uri: str, player_id: str, username: str):
    global connected

    while True:
        try:
            async with websockets.connect(uri) as ws:
                connected = True
                await ws.send(json.dumps({"type": "join", "id": player_id, "username": username}))

                async def receiver():
                    async for msg in ws:
                        receive_queue.put(json.loads(msg))

                async def sender():
                    while connected:
                        if not send_queue.empty():
                            await ws.send(json.dumps(send_queue.get()))
                        await asyncio.sleep(0.01)

                await asyncio.gather(receiver(), sender())
        except Exception as e:
                print(f"WebSocket Connection Failed: {e}") 
        finally:
                connected = False

        await asyncio.sleep(2)


def start_network_thread(uri: str, player_id: str = "player_1", username: str = "Guest"):
    def run_network():
        asyncio.run(_network_loop(uri, player_id, username))

    threading.Thread(target=run_network, daemon=True).start()


def send_input(input_dict: dict):
    send_queue.put({"type": "input", **input_dict})


def send_ping():
    send_queue.put({"type": "ping"})


def get_latest_state() -> dict | None:
    latest = None
    while True:
        try:
            latest = receive_queue.get_nowait()
        except queue.Empty:
            return latest


def is_connected() -> bool:
    return connected