from config.config import BoardConfig

# כיוון "קדימה" לרגלי לפי צבע:
# w (לבן) זז ל-row נמוך יותר (-1), b (שחור) ל-row גבוה יותר (+1)
_PAWN_FORWARD = {'w': -1, 'b': 1}


class MoveContext:
    """
    מחלקה שמרכזת את כל המידע על מהלך אחד.
    במקום להעביר grid + 4 קואורדינטות בכל פעם, שולחים אובייקט אחד.
    """
    def __init__(self, grid, from_row: int, from_col: int, to_row: int, to_col: int):
        self.grid = grid
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col

    @property
    def from_token(self) -> str:
        """הטוקן במשבצת המקור, למשל 'wR'."""
        return self.grid[self.from_row][self.from_col]

    @property
    def to_token(self) -> str:
        """הטוקן במשבצת היעד — '.' אם ריק, או כלי כמו 'bK'."""
        return self.grid[self.to_row][self.to_col]

    @property
    def color(self) -> str:
        """צבע הכלי הנע: 'w' או 'b' (התו הראשון בטוקן)."""
        return self.from_token[0]

    @property
    def row_delta(self) -> int:
        """שינוי בשורה עם סימן: שלילי = למעלה, חיובי = למטה."""
        return self.to_row - self.from_row

    @property
    def col_delta(self) -> int:
        """שינוי בעמודה עם סימן: שלילי = שמאלה, חיובי = ימינה."""
        return self.to_col - self.from_col

    @property
    def d_row(self) -> int:
        """מרחק בשורות (תמיד חיובי)."""
        return abs(self.row_delta)

    @property
    def d_col(self) -> int:
        """מרחק בעמודות (תמיד חיובי)."""
        return abs(self.col_delta)

    def is_same_square(self) -> bool:
        """לא ניתן 'להיזוז' לאותה משבצת."""
        return self.d_row == 0 and self.d_col == 0

    def is_destination_empty(self) -> bool:
        """האם משבצת היעד ריקה."""
        return self.to_token == BoardConfig.EMPTY_CELL

    def is_destination_blocked_by_ally(self) -> bool:
        """אסור לנחות על כלי מאותו צבע (בעל ברית)."""
        if self.is_destination_empty():
            return False

        return self.from_token[0] == self.to_token[0]

    def is_path_clear(self) -> bool:
        """
        בודק שאין כלים בדרך בין המקור ליעד (לא כולל שתי הקצוות).
        רלוונטי לצריח, רץ ומלכה — לא לפרש ולא לרגלי.
        """
        row_step = self.row_delta
        col_step = self.col_delta

        if row_step:
            row_step //= abs(row_step)
        if col_step:
            col_step //= abs(col_step)

        current_row = self.from_row + row_step
        current_col = self.from_col + col_step

        while current_row != self.to_row or current_col != self.to_col:
            if self.grid[current_row][current_col] != BoardConfig.EMPTY_CELL:
                return False
            current_row += row_step
            current_col += col_step

        return True


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
    - צעד אחד באלכסון קדימה → רק אכילה (היעד חייב להכיל אויב)
    - אסור לזוז 2 משבצות, אסור לאכול קדימה ישר
    """
    forward = _PAWN_FORWARD[move.color]

    # תנועה קדימה ישרה (בלי שינוי עמודה)
    if move.col_delta == 0 and move.row_delta == forward:
        return move.is_destination_empty()

    # אכילה באלכסון קדימה (שינוי עמודה של 1)
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
