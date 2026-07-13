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

    def pawn_forward_row_delta(self) -> int:
        """כיוון הקדימה של רגלי לפי הצבע שלו."""
        return _PAWN_FORWARD[self.color]

    def is_pawn_start_row(self) -> bool:
        """האם הרגלי נמצא בשורת ההתחלה שלו."""
        rows = len(self.grid)
        if self.color == 'w':
            return self.from_row == rows - 2
        return self.from_row == (1 if rows >= 5 else 0)

    def is_pawn_double_path_clear(self) -> bool:
        """האם המשבצת באמצע מהלך כפול (2 תאים) פנויה."""
        mid_row = self.from_row + self.pawn_forward_row_delta()
        return self.grid[mid_row][self.from_col] == BoardConfig.EMPTY_CELL
