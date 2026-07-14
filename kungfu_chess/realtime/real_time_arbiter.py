from kungfu_chess import constants
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.position import Position
from kungfu_chess.realtime.jump import Jump
from kungfu_chess.realtime.motion import Motion


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


class RealTimeArbiter:
    def __init__(self):
        self.current_time = 0
        self.active_motions = {}
        self.active_jumps = {}
        self._move_order = 0

    def has_active_motion_from(self, row: int, col: int) -> bool:
        return (row, col) in self.active_motions

    def has_any_active_motion(self) -> bool:
        return len(self.active_motions) > 0

    def advance_time(self, game_state: GameState, ms: int):
        self.current_time += ms
        self._complete_due_motions(game_state)

    def start_motion(self, game_state: GameState, from_row, from_col, to_row, to_col, piece_token, duration):
        self._move_order += 1
        piece = game_state.board.piece_at(Position(from_row, from_col))
        piece_id = piece.id if piece else 0
        self.active_motions[(from_row, from_col)] = Motion(
            piece_id, piece_token, from_row, from_col, to_row, to_col,
            self.current_time, duration, self._move_order
        )

    def start_jump(self, game_state: GameState, row: int, col: int, piece_token: str):
        self.active_jumps[(row, col)] = Jump(piece_token, row, col, self.current_time)

    def has_opposite_color_route_conflict(
        self, game_state: GameState, piece_color: str,
        from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        for active in self.active_motions.values():
            if active.piece_token[0] == piece_color:
                continue
            if self._is_mutual_enemy_collision(from_row, from_col, to_row, to_col, piece_color, active):
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

    @staticmethod
    def _is_mutual_enemy_collision(from_row, from_col, to_row, to_col, piece_color, other: Motion) -> bool:
        if other.piece_token[0] == piece_color:
            return False
        return (
            (to_row, to_col) == (other.from_row, other.from_col)
            and (other.to_row, other.to_col) == (from_row, from_col)
        )

    def _is_airborne_at(self, row: int, col: int):
        jump = self.active_jumps.get((row, col))
        if jump and self.current_time <= jump.end_time:
            return jump
        return None

    def _expire_due_jumps(self):
        expired = [key for key, jump in self.active_jumps.items() if self.current_time > jump.end_time]
        for key in expired:
            del self.active_jumps[key]

    def _apply_motion(self, game_state: GameState, motion: Motion) -> bool:
        airborne = self._is_airborne_at(motion.to_row, motion.to_col)
        if airborne and airborne.piece_token[0] != motion.piece_token[0]:
            game_state.board.remove_piece(Position(motion.from_row, motion.from_col))
            if motion.piece_token[1] == 'K':
                game_state.game_over = True
                self.active_motions.clear()
                self.active_jumps.clear()
                return True
            return False

        source = Position(motion.from_row, motion.from_col)
        destination = Position(motion.to_row, motion.to_col)
        captured = game_state.board.piece_at(destination)
        new_kind = None
        if motion.piece_token[1] == 'P':
            if motion.piece_token[0] == 'w' and motion.to_row == 0:
                new_kind = 'Q'
            elif motion.piece_token[0] == 'b' and motion.to_row == game_state.board.height - 1:
                new_kind = 'Q'

        game_state.board.move_piece(source, destination, new_kind)

        if captured is not None and captured.kind == 'K':
            game_state.game_over = True
            self.active_motions.clear()
            return True
        return False

    def _complete_due_motions(self, game_state: GameState):
        due_motions = [
            self.active_motions.pop(key)
            for key, motion in list(self.active_motions.items())
            if self.current_time >= motion.arrival_time
        ]
        if not due_motions:
            return

        due_motions.sort(key=lambda move: (move.start_time, move.order))
        cancelled = set()
        for i, motion in enumerate(due_motions):
            if i in cancelled:
                continue
            for j in range(i + 1, len(due_motions)):
                if j in cancelled:
                    continue
                other = due_motions[j]
                if motion.piece_token[0] == other.piece_token[0]:
                    continue
                if (
                    (motion.to_row, motion.to_col) == (other.from_row, other.from_col)
                    and (other.to_row, other.to_col) == (motion.from_row, motion.from_col)
                ):
                    cancelled.add(j)

        for i, motion in enumerate(due_motions):
            if game_state.game_over:
                break
            if i not in cancelled:
                self._apply_motion(game_state, motion)

        self._expire_due_jumps()

    def complete_pending(self, game_state: GameState):
        self._complete_due_motions(game_state)
