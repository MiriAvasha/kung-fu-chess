from model.piece import Piece
from model.position import Position
from rules.promotion import (
    DEFAULT_PROMOTION_SERVICE,
    PawnToQueenPromotion,
    PromotionService,
)
from tests.conftest import make_board


class TestPromotion:
    def test_white_pawn_promotes_on_row_0(self):
        board = make_board([['.'], ['wP']])
        piece = board.piece_at(Position(1, 0))
        assert PawnToQueenPromotion().promoted_kind(board, piece, Position(0, 0)) == 'Q'

    def test_black_pawn_promotes_on_last_row(self):
        board = make_board([['bP'], ['.']])
        piece = board.piece_at(Position(0, 0))
        assert PawnToQueenPromotion().promoted_kind(board, piece, Position(1, 0)) == 'Q'

    def test_non_pawn_does_not_promote(self):
        board = make_board([['.'], ['wR']])
        piece = board.piece_at(Position(1, 0))
        assert PawnToQueenPromotion().promoted_kind(board, piece, Position(0, 0)) is None

    def test_pawn_not_on_last_rank(self):
        board = make_board([['.'], ['.'], ['wP']])
        piece = board.piece_at(Position(2, 0))
        assert PawnToQueenPromotion().promoted_kind(board, piece, Position(1, 0)) is None

    def test_default_service_resolves_queen(self):
        board = make_board([['.'] * 8 for _ in range(8)])
        piece = Piece('w', 'P', Position(1, 0))
        assert DEFAULT_PROMOTION_SERVICE.resolve(board, piece, Position(0, 0)) == 'Q'

    def test_empty_service_returns_none(self):
        board = make_board([['.'], ['wP']])
        piece = board.piece_at(Position(1, 0))
        assert PromotionService([]).resolve(board, piece, Position(0, 0)) is None
