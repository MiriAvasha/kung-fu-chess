from kungfu_chess.model.board import Board
from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position
from kungfu_chess.rules.helpers import collect_sliding_destinations


class RookRule:
    def legal_destinations(self, board: Board, piece: Piece) -> set:
        destinations = set()
        for row_step, col_step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            destinations |= collect_sliding_destinations(board, piece, row_step, col_step)
        return destinations
