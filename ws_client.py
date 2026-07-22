import asyncio

import websockets


async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = "Hello from client!"
        await websocket.send(message)
        print(f"Sent: {message}")

        response = await websocket.recv()
        print(f"Echo: {response}")


if __name__ == "__main__":
    asyncio.run(main())
