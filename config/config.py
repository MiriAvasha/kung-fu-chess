class BoardConfig:
    """
    ריכוז כל חוקי התצורה היבשים וההגדרות של הלוח.
    """
    EMPTY_CELL = '.'
    VALID_COLORS = {'w', 'b'}
    VALID_PIECES = {'K', 'Q', 'R', 'B', 'N', 'P'}
    MS_PER_CELL = 1000
    JUMP_DURATION = 1000

    PIECE_SPEEDS = {
        'P': 1000,
        'R': 1000,
        'B': 1000,
        'N': 1000,
        'Q': 1000,
        'K': 1000,
    }

    @classmethod
    def get_speed_for_piece(cls, piece_type: str) -> int:
        return cls.PIECE_SPEEDS.get(piece_type, cls.MS_PER_CELL)

    @classmethod
    def is_valid_token(cls, token: str) -> bool:
        # אם זו משבצת ריקה - זה תקין
        if token == cls.EMPTY_CELL:
            return True

        # כלי חייב להיות בדיוק באורך 2 תווים (למשל wK)
        if len(token) != 2:
            return False

        color = token[0]
        piece = token[1]

        return color in cls.VALID_COLORS and piece in cls.VALID_PIECES