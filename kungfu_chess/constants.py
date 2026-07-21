from enum import Enum


EMPTY_CELL = '.'
FIRST_ROW = 0


class PieceColor(str, Enum):
    WHITE = 'w'
    BLACK = 'b'


VALID_COLORS = frozenset(color.value for color in PieceColor)

class PieceKind(str, Enum):
    KING = 'K'
    QUEEN = 'Q'
    ROOK = 'R'
    BISHOP = 'B'
    KNIGHT = 'N'
    PAWN = 'P'


VALID_PIECES = frozenset(piece.value for piece in PieceKind)
CELL_SIZE = 100
MS_PER_CELL = 1000
JUMP_DURATION = 1000

PAWN_FORWARD = {PieceColor.WHITE.value: -1, PieceColor.BLACK.value: 1}
PIECE_SPEEDS = {
    PieceKind.PAWN.value: 1000,
    PieceKind.ROOK.value: 1000,
    PieceKind.BISHOP.value: 1000,
    PieceKind.KNIGHT.value: 1000,
    PieceKind.QUEEN.value: 1000,
    PieceKind.KING.value: 1000,
}

def get_speed_for_piece(piece_type: str) -> int:
    return PIECE_SPEEDS.get(piece_type, MS_PER_CELL)


def is_valid_token(token: str) -> bool:
    if token == EMPTY_CELL:
        return True
    if len(token) != 2:
        return False
    return token[0] in VALID_COLORS and token[1] in VALID_PIECES
