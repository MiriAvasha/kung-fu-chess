from rules.move_context import MoveContext


def validate_king(move: MoveContext) -> bool:
    """מלך: צעד אחד לכל כיוון."""
    return move.d_row <= 1 and move.d_col <= 1

def validate_rook(move: MoveContext) -> bool:
    """צריח: תנועה ישרה בשורה או בעמודה."""
    return move.d_row == 0 or move.d_col == 0

def validate_bishop(move: MoveContext) -> bool:
    """רץ: תנועה באלכסון."""
    return move.d_row == move.d_col

def validate_queen(move: MoveContext) -> bool:
    """מלכה: ישר או אלכסון."""
    return move.d_row == 0 or move.d_col == 0 or move.d_row == move.d_col

def validate_knight(move: MoveContext) -> bool:
    """פרש: קפיצה ב-L — יכול לדלג מעל כלים."""
    return (move.d_row == 2 and move.d_col == 1) or (move.d_row == 1 and move.d_col == 2)

def validate_pawn(move: MoveContext) -> bool:
    """
    רגלי:
    - צעד אחד קדימה ישר → רק למשבצת ריקה
    - שני צעדים קדימה מהשורה הראשונה → מסלול פנוי + יעד ריק
    - צעד אחד באלכסון קדימה → רק אכילה (היעד חייב להכיל אויב)
    - אסור לאכול קדימה ישר
    """
    forward = move.pawn_forward_row_delta()

    if move.col_delta == 0 and move.row_delta == forward:
        return move.is_destination_empty()

    if move.col_delta == 0 and move.row_delta == 2 * forward:
        return (
            move.is_pawn_start_row()
            and move.is_pawn_double_path_clear()
            and move.is_destination_empty()
        )

    if abs(move.col_delta) == 1 and move.row_delta == forward:
        return not move.is_destination_empty()

    return False


class MoveValidator:
    """
    מנהל את חוקי התנועה של הכלים בצורה גנרית.
    כל כלי ממופה לפונקציית בדיקה אחת ב-_MOVEMENT_RULES.
    """
    _MOVEMENT_RULES = {
        'K': validate_king,
        'R': validate_rook,
        'B': validate_bishop,
        'Q': validate_queen,
        'N': validate_knight,
        'P': validate_pawn,
    }

    # כלים שצריכים בדיקת מסלול פנוי בנוסף לבדיקת כיוון
    _SLIDING_PIECES = frozenset({'R', 'B', 'Q'})

    @classmethod
    def is_move_legal_for_piece(cls, piece_type: str, move: MoveContext) -> bool:
        # 1. לא נשארים באותה משבצת
        if move.is_same_square():
            return False

        # 2. לא נוחתים על בעל ברית (תקף לכל הכלים)
        if move.is_destination_blocked_by_ally():
            return False

        # 3. בדיקת כיוון/סוג תנועה לפי סוג הכלי
        validator_func = cls._MOVEMENT_RULES.get(piece_type)
        if not validator_func or not validator_func(move):
            return False

        # 4. בדיקת מסלול פנוי — רק לכלים "מחליקים"
        if piece_type in cls._SLIDING_PIECES and not move.is_path_clear():
            return False

        return True
