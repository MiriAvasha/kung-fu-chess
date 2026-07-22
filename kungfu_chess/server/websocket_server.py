import asyncio
import contextlib
import time
from typing import Any, Optional, Set

import websockets
from websockets.exceptions import ConnectionClosed

from engine.game_factory import build_engine
from server.game_session import GameSession
from shared.protocol import encode_message, error_message


HOST = 'localhost'
PORT = 8765
TICK_SECONDS = 0.05


class GameServer:
    def __init__(self, session: Optional[GameSession] = None):
        self.session = session or GameSession(build_engine())
        self.clients: Set[Any] = set()

    async def handle_client(self, websocket):
        self.clients.add(websocket)
        print('Client connected')
        try:
            await self._send(websocket, self.session.initial_message())
            async for raw_message in websocket:
                if not isinstance(raw_message, str):
                    await self._send(
                        websocket,
                        error_message(
                            'invalid_command',
                            'move command must be text',
                        ),
                    )
                    continue

                result = self.session.handle_command(raw_message)
                await self._send(websocket, result)
                if (
                    result.get('type') == 'move_result'
                    and result.get('accepted')
                ):
                    await self.broadcast_game_state()
        except ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print('Client disconnected')

    async def run_ticker(self):
        previous = time.monotonic()
        while True:
            await asyncio.sleep(TICK_SECONDS)
            current = time.monotonic()
            elapsed_ms = max(1, int((current - previous) * 1000))
            previous = current
            if self.session.advance(elapsed_ms):
                await self.broadcast_game_state()

    async def broadcast_game_state(self):
        if not self.clients:
            return

        encoded = encode_message(self.session.game_state_message())
        disconnected = set()
        for client in tuple(self.clients):
            try:
                await client.send(encoded)
            except ConnectionClosed:
                disconnected.add(client)
        self.clients.difference_update(disconnected)

    async def _send(self, websocket, message):
        await websocket.send(encode_message(message))


async def main(host: str = HOST, port: int = PORT):
    game_server = GameServer()
    ticker = asyncio.create_task(game_server.run_ticker())
    try:
        async with websockets.serve(
            game_server.handle_client,
            host,
            port,
        ):
            print(f'WebSocket server running on ws://{host}:{port}')
            await asyncio.Future()
    finally:
        ticker.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ticker
