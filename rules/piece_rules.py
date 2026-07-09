from config.config import BoardConfig


class MoveContext:
    def __init__(self, grid, from_row: int, from_col: int, to_row: int, to_col: int):
        self.grid = grid
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col

    @property
    def from_token(self) -> str:
        return self.grid[self.from_row][self.from_col]

    @property
    def to_token(self) -> str:
        return self.grid[self.to_row][self.to_col]

    @property
    def d_row(self) -> int:
        return abs(self.to_row - self.from_row)

    @property
    def d_col(self) -> int:
        return abs(self.to_col - self.from_col)

    def is_same_square(self) -> bool:
        return self.d_row == 0 and self.d_col == 0

    def is_destination_blocked_by_ally(self) -> bool:
        if self.to_token == BoardConfig.EMPTY_CELL:
            return False

        return self.from_token[0] == self.to_token[0]

    def is_path_clear(self) -> bool:
        row_step = self.to_row - self.from_row
        col_step = self.to_col - self.from_col

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


def validate_king(d_row: int, d_col: int) -> bool:
    return d_row <= 1 and d_col <= 1

def validate_rook(d_row: int, d_col: int) -> bool:
    return d_row == 0 or d_col == 0

def validate_bishop(d_row: int, d_col: int) -> bool:
    return d_row == d_col

def validate_queen(d_row: int, d_col: int) -> bool:
    return d_row == 0 or d_col == 0 or d_row == d_col

def validate_knight(d_row: int, d_col: int) -> bool:
    return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)


class MoveValidator:
    """
    מנהל את חוקי התנועה של הכללים בצורה גנרית.
    """
    _MOVEMENT_RULES = {
        'K': validate_king,
        'R': validate_rook,
        'B': validate_bishop,
        'Q': validate_queen,
        'N': validate_knight
    }

    _SLIDING_PIECES = frozenset({'R', 'B', 'Q'})

    @classmethod
    def is_move_legal_for_piece(cls, piece_type: str, move: MoveContext) -> bool:
        if move.is_same_square():
            return False

        if move.is_destination_blocked_by_ally():
            return False

        validator_func = cls._MOVEMENT_RULES.get(piece_type)
        if not validator_func or not validator_func(move.d_row, move.d_col):
            return False

        if piece_type in cls._SLIDING_PIECES and not move.is_path_clear():
            return False

        return True
