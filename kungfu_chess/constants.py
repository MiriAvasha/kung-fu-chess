from typing import Literal, get_args

EMPTY_CELL = '.'
VALID_COLORS = {'w', 'b'}
PieceKind = Literal['K', 'Q', 'R', 'B', 'N', 'P']
VALID_PIECES = frozenset(get_args(PieceKind))
CELL_SIZE = 100
MS_PER_CELL = 1000
JUMP_DURATION = 1000

PAWN_FORWARD = {'w': -1, 'b': 1}
# כמה שורות מהקצה הרגלי יכול לבצע צעד כפול
PAWN_START_ROW_OFFSET = 1

PIECE_SPEEDS = {
    'P': 1000,
    'R': 1000,
    'B': 1000,
    'N': 1000,
    'Q': 1000,
    'K': 1000,
}


def get_speed_for_piece(piece_type: str) -> int:
    return PIECE_SPEEDS.get(piece_type, MS_PER_CELL)


def is_valid_token(token: str) -> bool:
    if token == EMPTY_CELL:
        return True
    if len(token) != 2:
        return False
    return token[0] in VALID_COLORS and token[1] in VALID_PIECES
