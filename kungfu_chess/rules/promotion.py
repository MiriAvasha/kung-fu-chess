from typing import List, Optional

from model.board import Board
from model.piece import Piece
from model.position import Position


class PromotionRule:
    """Extend this to add new promotion cases without touching move/apply code."""

    def promoted_kind(self, board: Board, piece: Piece, destination: Position) -> Optional[str]:
        raise NotImplementedError


class PawnToQueenPromotion(PromotionRule):
    def promoted_kind(self, board: Board, piece: Piece, destination: Position) -> Optional[str]:
        if piece.kind != 'P':
            return None
        if piece.color == 'w' and destination.row == 0:
            return 'Q'
        if piece.color == 'b' and destination.row == board.height - 1:
            return 'Q'
        return None


class PromotionService:
    def __init__(self, rules: Optional[List[PromotionRule]] = None):
        self.rules = list(rules) if rules is not None else [PawnToQueenPromotion()]

    def resolve(self, board: Board, piece: Piece, destination: Position) -> Optional[str]:
        for rule in self.rules:
            kind = rule.promoted_kind(board, piece, destination)
            if kind is not None:
                return kind
        return None


DEFAULT_PROMOTION_SERVICE = PromotionService()
