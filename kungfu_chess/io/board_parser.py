import sys

from kungfu_chess import constants
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState


class BoardParser:
    def __init__(self):
        self._width = None
        self._rows = []

    def add_row(self, row_str: str) -> GameState:
        tokens = row_str.strip().split()
        if not tokens:
            return GameState(Board.from_token_rows(self._rows))

        if self._width is None:
            self._width = len(tokens)
        elif len(tokens) != self._width:
            print("ERROR ROW_WIDTH_MISMATCH")
            sys.exit(0)

        for token in tokens:
            if not constants.is_valid_token(token):
                print("ERROR UNKNOWN_TOKEN")
                sys.exit(0)

        self._rows.append(tokens)
        return GameState(Board.from_token_rows(self._rows))
