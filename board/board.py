import sys
from config.config import BoardConfig
from rules.move_context import MoveContext
from rules.move_validator import MoveValidator


class ActiveMove:
    def __init__(self, piece, from_row, from_col, to_row, to_col, start_time, duration):
        self.piece = piece
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.start_time = start_time
        self.duration = duration

    @property
    def arrival_time(self) -> int:
        return self.start_time + self.duration


class ChessBoard:
    def __init__(self):
        self.grid = []
        self.width = None
        self.selected_piece = None
        self.current_time = 0
        self.active_moves = {}

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

    def _is_moving_from(self, row: int, col: int) -> bool:
        return (row, col) in self.active_moves

    def _complete_due_moves(self):
        completed_keys = [
            key for key, active_move in self.active_moves.items()
            if self.current_time >= active_move.arrival_time
        ]

        for key in completed_keys:
            active_move = self.active_moves.pop(key)
            self.grid[active_move.to_row][active_move.to_col] = active_move.piece
            self.grid[active_move.from_row][active_move.from_col] = BoardConfig.EMPTY_CELL

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
                duration = max(move.d_row, move.d_col) * BoardConfig.get_speed_for_piece(piece_type)
                self.active_moves[(from_row, from_col)] = ActiveMove(
                    piece, from_row, from_col, row, col, self.current_time, duration
                )

            self.selected_piece = None
        elif clicked_token != BoardConfig.EMPTY_CELL:
            if self._is_moving_from(row, col):
                return

            self.selected_piece = (row, col)

    def advance_clock(self, ms: int):
        self.current_time += ms
        self._complete_due_moves()

    def print_board(self):
        for row in self.grid:
            print(" ".join(row))
