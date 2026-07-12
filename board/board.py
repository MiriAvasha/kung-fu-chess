import sys
from config.config import BoardConfig
from rules.move_context import MoveContext
from rules.move_validator import MoveValidator

class ChessBoard:
    def __init__(self):
        self.grid = []
        self.width = None
        self.selected_piece = None
        self.clock = 0

    def add_row(self, row_str: str):
        tokens = row_str.strip().split()
        if not tokens:
            return

        if self.width is None:
            self.width = len(tokens)
        elif len(tokens) != self.width:
            print("ERROR ROW_WIDTH_MISMATCH")
            sys.exit(0)

        for token in tokens:
            if not BoardConfig.is_valid_token(token):
                print("ERROR UNKNOWN_TOKEN")
                sys.exit(0)

        self.grid.append(tokens)

    def handle_click(self, x: int, y: int):
        col = x // 100
        row = y // 100

        if row < 0 or row >= len(self.grid) or col < 0 or col >= self.width:
            return

        clicked_token = self.grid[row][col]

        if self.selected_piece is not None:
            from_row, from_col = self.selected_piece
            piece = self.grid[from_row][from_col]
            piece_type = piece[1]

            move = MoveContext(self.grid, from_row, from_col, row, col)
            if MoveValidator.is_move_legal_for_piece(piece_type, move):
                self.grid[row][col] = piece
                self.grid[from_row][from_col] = BoardConfig.EMPTY_CELL

            self.selected_piece = None
        elif clicked_token != BoardConfig.EMPTY_CELL:
            self.selected_piece = (row, col)

    def advance_clock(self, ms: int):
        self.clock += ms

    def print_board(self):
        for row in self.grid:
            print(" ".join(row))