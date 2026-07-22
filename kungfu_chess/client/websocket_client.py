import asyncio

import websockets
from websockets.exceptions import ConnectionClosed

from client.terminal_ui import display_message


URI = 'ws://localhost:8765'


async def send_commands(websocket):
    loop = asyncio.get_running_loop()
    while True:
        command = await loop.run_in_executor(
            None,
            input,
            'Move (for example WPe2e4, or /quit): ',
        )
        command = command.strip()
        if command.lower() == '/quit':
            return
        if command:
            await websocket.send(command)


async def receive_messages(websocket):
    async for raw_message in websocket:
        display_message(raw_message)


async def main(uri: str = URI):
    try:
        async with websockets.connect(uri) as websocket:
            print(f'Connected to {uri}')
            receiver = asyncio.create_task(receive_messages(websocket))
            sender = asyncio.create_task(send_commands(websocket))
            done, pending = await asyncio.wait(
                {receiver, sender},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for task in done:
                task.result()
    except ConnectionClosed:
        print('Connection to server closed.')
    except OSError as error:
        print(f'Could not connect to {uri}: {error}')
