from model.board import Board
from model.piece import Piece
from model.position import Position


_PAWN_FORWARD = {'w': -1, 'b': 1}


class PawnRule:
    def legal_destinations(self, board: Board, piece: Piece) -> set:
        destinations = set()
        forward = _PAWN_FORWARD[piece.color]
        one_step = Position(piece.cell.row + forward, piece.cell.col)
        if board.is_inside(one_step) and board.piece_at(one_step) is None:
            destinations.add(one_step)
            if self._is_start_row(board, piece):
                two_step = Position(piece.cell.row + 2 * forward, piece.cell.col)
                mid = Position(piece.cell.row + forward, piece.cell.col)
                if (
                    board.is_inside(two_step)
                    and board.piece_at(mid) is None
                    and board.piece_at(two_step) is None
                ):
                    destinations.add(two_step)

        for d_col in (-1, 1):
            capture = Position(piece.cell.row + forward, piece.cell.col + d_col)
            if not board.is_inside(capture):
                continue
            occupant = board.piece_at(capture)
            if occupant is not None and occupant.color != piece.color:
                destinations.add(capture)

        return destinations

    def _is_start_row(self, board: Board, piece: Piece) -> bool:
        if piece.color == 'w':
            return piece.cell.row == board.height - 2
        return piece.cell.row == (1 if board.height >= 5 else 0)
