import sys
from config.config import BoardConfig
from rules.move_context import MoveContext
from rules.move_validator import MoveValidator


def _get_route_columns(from_col: int, to_col: int) -> set:
    if from_col == to_col:
        return set()
    lo, hi = min(from_col, to_col), max(from_col, to_col)
    return set(range(lo + 1, hi + 1))


def _get_route_rows(from_row: int, to_row: int) -> set:
    if from_row == to_row:
        return set()
    lo, hi = min(from_row, to_row), max(from_row, to_row)
    return set(range(lo + 1, hi + 1))


class ActiveMove:
    def __init__(self, piece, from_row, from_col, to_row, to_col, start_time, duration, order):
        self.piece = piece
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.start_time = start_time
        self.duration = duration
        self.order = order

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
        self._move_order = 0

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

    @staticmethod
    def _is_mutual_enemy_collision(
        from_row: int, from_col: int, to_row: int, to_col: int,
        piece_color: str, other: ActiveMove
    ) -> bool:
        if other.piece[0] == piece_color:
            return False

        return (
            (to_row, to_col) == (other.from_row, other.from_col)
            and (other.to_row, other.to_col) == (from_row, from_col)
        )

    def _has_opposite_color_route_conflict(
        self, piece_color: str, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        for active in self.active_moves.values():
            if active.piece[0] == piece_color:
                continue

            if self._is_mutual_enemy_collision(
                from_row, from_col, to_row, to_col, piece_color, active
            ):
                continue

            new_cols = _get_route_columns(from_col, to_col)
            new_rows = _get_route_rows(from_row, to_row)
            active_cols = _get_route_columns(active.from_col, active.to_col)
            active_rows = _get_route_rows(active.from_row, active.to_row)

            same_row_horizontal = (
                from_row == to_row
                and active.from_row == active.to_row
                and from_row == active.from_row
            )
            same_col_vertical = (
                from_col == to_col
                and active.from_col == active.to_col
                and from_col == active.from_col
            )

            if same_row_horizontal and new_cols & active_cols:
                return True

            if same_col_vertical and new_rows & active_rows:
                return True

        return False

    def _apply_move(self, active_move: ActiveMove):
        self.grid[active_move.to_row][active_move.to_col] = active_move.piece
        self.grid[active_move.from_row][active_move.from_col] = BoardConfig.EMPTY_CELL

    def _complete_due_moves(self):
        due_moves = [
            self.active_moves.pop(key)
            for key, active_move in list(self.active_moves.items())
            if self.current_time >= active_move.arrival_time
        ]

        if not due_moves:
            return

        due_moves.sort(key=lambda move: (move.start_time, move.order))
        cancelled = set()

        for i, move in enumerate(due_moves):
            if i in cancelled:
                continue
            for j in range(i + 1, len(due_moves)):
                if j in cancelled:
                    continue
                other = due_moves[j]
                if move.piece[0] == other.piece[0]:
                    continue
                if (
                    (move.to_row, move.to_col) == (other.from_row, other.from_col)
                    and (other.to_row, other.to_col) == (move.from_row, move.from_col)
                ):
                    cancelled.add(j)

        for i, move in enumerate(due_moves):
            if i not in cancelled:
                self._apply_move(move)

    def handle_click(self, x: int, y: int):
        self._complete_due_moves()

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
                if not self._has_opposite_color_route_conflict(
                    piece[0], from_row, from_col, row, col
                ):
                    duration = max(move.d_row, move.d_col) * BoardConfig.get_speed_for_piece(piece_type)
                    self._move_order += 1
                    self.active_moves[(from_row, from_col)] = ActiveMove(
                        piece, from_row, from_col, row, col,
                        self.current_time, duration, self._move_order
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
