import asyncio
import json

import websockets

from server.websocket_server import GameServer


async def receive_json(websocket):
    raw_message = await asyncio.wait_for(websocket.recv(), timeout=2)
    return json.loads(raw_message)


async def websocket_game_scenario():
    game_server = GameServer()
    async with websockets.serve(
        game_server.handle_client,
        '127.0.0.1',
        0,
    ) as running_server:
        port = running_server.sockets[0].getsockname()[1]
        uri = f'ws://127.0.0.1:{port}'

        async with websockets.connect(uri) as first_client:
            first_initial = await receive_json(first_client)
            async with websockets.connect(uri) as second_client:
                second_initial = await receive_json(second_client)
                assert first_initial == second_initial

                await first_client.send('WPe2e4')
                move_result = await receive_json(first_client)
                first_update = await receive_json(first_client)
                second_update = await receive_json(second_client)

                assert move_result['type'] == 'move_result'
                assert move_result['accepted'] is True
                assert first_update == second_update
                assert first_update['type'] == 'game_state'
                assert first_update['state']['active_motions']

                game_server.session.advance(10000)
                await game_server.broadcast_game_state()
                first_arrival = await receive_json(first_client)
                second_arrival = await receive_json(second_client)

                assert first_arrival == second_arrival
                assert first_arrival['state']['board'][4][4] == 'wP'
                assert first_arrival['state']['active_motions'] == []


def test_two_clients_receive_the_same_authoritative_state():
    asyncio.run(websocket_game_scenario())
