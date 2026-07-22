import asyncio

import websockets


async def handler(websocket):
    print("Client connected")
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(message)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
