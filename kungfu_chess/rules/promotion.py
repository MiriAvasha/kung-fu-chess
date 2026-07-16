from typing import List, Optional

from constants import VALID_PIECES, PieceKind
from model.board import Board
from model.piece import Piece
from model.position import Position


class PromotionRule:
    """Extend this to add new promotion cases without touching move/apply code.

    Implementors must return a PieceKind from VALID_PIECES, or None when
    this rule does not apply (so callers can safely ignore it).
    """

    def promoted_kind(self, board: Board, piece: Piece, destination: Position) -> Optional[PieceKind]:
        raise NotImplementedError


class PawnToQueenPromotion(PromotionRule):
    def promoted_kind(self, board: Board, piece: Piece, destination: Position) -> Optional[PieceKind]:
        if piece.kind != 'P':
            return None
        if piece.color == 'w' and destination.row == 0:
            return 'Q'
        if piece.color == 'b' and destination.row == board.height - 1:
            return 'Q'
        return None


class PromotionService:
    def __init__(self, rules: List[PromotionRule]):
        self.rules = list(rules)

    def resolve(self, board: Board, piece: Piece, destination: Position) -> Optional[PieceKind]:
        for rule in self.rules:
            kind = rule.promoted_kind(board, piece, destination)
            if kind is not None and kind in VALID_PIECES:
                return kind
        return None


# אנחנו מגדירים את החוקים הפעילים כאן כדי לשמור על פשטות (KISS).
# הוספת חוק הכתרה חדש מתבצעת בנקודה אחת בלבד (כאן), מבלי לפצל את הלוגיקה
# לקבצים מרובים ולייצר מורכבות של Imports.
ACTIVE_PROMOTION_RULES = [PawnToQueenPromotion()]
DEFAULT_PROMOTION_SERVICE = PromotionService(ACTIVE_PROMOTION_RULES)
