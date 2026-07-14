from typing import Optional

from kungfu_chess.model.board import Board


class GameState:
    def __init__(self, board: Optional[Board] = None):
        self.board = board if board is not None else Board()
        self.game_over = False
