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

    @classmethod
    def is_move_legal_for_piece(cls, piece_type: str, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)

        if d_row == 0 and d_col == 0:
            return False

        validator_func = cls._MOVEMENT_RULES.get(piece_type)
        if validator_func:
            return validator_func(d_row, d_col)

        return False