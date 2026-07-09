class BoardConfig:
    """
    ריכוז כל חוקי התצורה היבשים וההגדרות של הלוח.
    """
    EMPTY_CELL = '.'
    VALID_COLORS = {'w', 'b'}
    VALID_PIECES = {'K', 'Q', 'R', 'B', 'N', 'P'}

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