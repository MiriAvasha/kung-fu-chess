from kungfu_chess.rules.pieces.bishop_rule import BishopRule
from kungfu_chess.rules.pieces.king_rule import KingRule
from kungfu_chess.rules.pieces.knight_rule import KnightRule
from kungfu_chess.rules.pieces.pawn_rule import PawnRule
from kungfu_chess.rules.pieces.queen_rule import QueenRule
from kungfu_chess.rules.pieces.rook_rule import RookRule

PIECE_RULES = {
    'R': RookRule(),
    'B': BishopRule(),
    'Q': QueenRule(),
    'N': KnightRule(),
    'K': KingRule(),
    'P': PawnRule(),
}
