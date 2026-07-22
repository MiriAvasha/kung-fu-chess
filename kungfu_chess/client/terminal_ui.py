from typing import Any, Dict

from shared.protocol import decode_message


def print_board(state: Dict[str, Any]):
    board = state['board']
    height = state['board_height']
    width = state['board_width']
    print()
    for row_index, row in enumerate(board):
        rank = height - row_index
        print(f"{rank}  {' '.join(row)}")
    files = ' '.join(chr(ord('a') + index) for index in range(width))
    print(f'   {files}')

    motions = state.get('active_motions', [])
    if motions:
        moving = ', '.join(
            '{} moving'.format(motion['piece'])
            for motion in motions
        )
        print(f'Active: {moving}')
    if state.get('game_over'):
        print('GAME OVER')
    print()


def display_message(raw_message: str):
    try:
        message = decode_message(raw_message)
    except (TypeError, ValueError):
        print(f'Server sent invalid JSON: {raw_message}')
        return

    message_type = message.get('type')
    if message_type == 'error':
        print(
            'Error [{}]: {}'.format(
                message.get('code'),
                message.get('message'),
            )
        )
        return

    if message_type == 'move_result':
        status = 'accepted' if message.get('accepted') else 'rejected'
        print(
            '{}: {} ({})'.format(
                message.get('command'),
                status,
                message.get('reason'),
            )
        )
        return

    if message_type in ('initial_state', 'game_state'):
        print_board(message['state'])
        return

    print(f'Unknown server message: {message}')
