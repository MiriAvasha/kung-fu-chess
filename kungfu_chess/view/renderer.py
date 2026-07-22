import os
import sys
from typing import Iterable, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants
from assets.piece_loader import PieceAssetLoader
from engine.results import GameSnapshot
from img import Img
from model.position import Position
from view.motion_layout import (
    idle_pixel_position,
    jump_pixel_position,
    jump_progress,
    motion_pixel_position,
    motion_progress,
    motion_source_cells,
)

SELECTED_BORDER_COLOR = (0, 255, 255, 255)
LEGAL_MOVE_DOT_COLOR = (70, 220, 70, 255)
GAME_OVER_BACKGROUND_COLOR = (35, 35, 190, 255)
GAME_OVER_TEXT_COLOR = (255, 255, 255, 255)
LONG_REST_BACKGROUND_COLOR = (0, 220, 255, 255)
AIRBORNE_BACKGROUND_COLOR = (255, 230, 150, 255)


class Renderer:
    """Builds an image from a read-only GameSnapshot."""

    def __init__(
        self,
        board_image_path: str = 'board.png',
        pieces_path: Optional[str] = None,
        cell_size: int = 100,
    ):
        self.board_image_path = board_image_path
        self.cell_size = cell_size
        self._board_cache = None
        self._board_cache_size = None

        if pieces_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pieces_path = os.path.join(base_dir, 'assets', 'pieces')
        self.piece_loader = PieceAssetLoader(pieces_path, cell_size=cell_size)

    def _cell_metrics(
        self,
        snapshot: GameSnapshot,
    ) -> Tuple[int, int, int]:
        if snapshot.board_width <= 0 or snapshot.board_height <= 0:
            raise ValueError('Snapshot board dimensions must be positive')

        return self.cell_size, self.cell_size, self.cell_size

    def _board_canvas(self, canvas_size) -> Img:
        if self._board_cache is None or self._board_cache_size != canvas_size:
            self._board_cache = Img().read(
                self.board_image_path,
                size=canvas_size,
            )
            self._board_cache_size = canvas_size
        return self._board_cache.copy()

    def long_rest_duration_ms(self, token: str) -> int:
        color, kind = token[0], token[1]
        piece_assets = self.piece_loader.load(color, kind)
        rest_state = piece_assets.get_state("long_rest")
        if rest_state is None:
            return 0
        return rest_state.animation_duration_ms

    def _piece_sprite(
        self,
        token: str,
        state_name: str = "idle",
        elapsed_ms: int = 0,
    ) -> Img:
        color, kind = token[0], token[1]
        piece_assets = self.piece_loader.load(color, kind)
        state = piece_assets.get_state(state_name)
        if state is None or not state.sprites:
            state = piece_assets.get_state("idle")
        if state is None or not state.sprites:
            raise FileNotFoundError(
                f"No usable sprite for {token}. "
                f"Available states: {sorted(piece_assets.states.keys())}"
            )
        frame_index = int(max(0, elapsed_ms) / 1000.0 * state.frames_per_sec)
        if state.is_loop:
            frame_index %= len(state.sprites)
        else:
            frame_index = min(frame_index, len(state.sprites) - 1)
        return state.sprites[frame_index]

    def render(
        self,
        snapshot: GameSnapshot,
        legal_destinations: Iterable = (),
        active_motions: Iterable = (),
        active_jumps: Iterable = (),
        active_long_rests: Iterable = (),
        current_time: int = 0,
        visual_time_ms: int = 0,
    ) -> Img:
        cell_w, cell_h, cell_size = self._cell_metrics(snapshot)
        canvas_size = (
            snapshot.board_width * cell_w,
            snapshot.board_height * cell_h,
        )
        board_canvas = self._board_canvas(canvas_size)
        self.piece_loader.set_cell_size(cell_size)
        motions = tuple(active_motions)
        jumps = tuple(active_jumps)
        long_rests = tuple(active_long_rests)
        moving_sources = motion_source_cells(motions)
        jumping_cells = {
            Position(jump.row, jump.col)
            for jump in jumps
        }
        rests_by_cell = {
            Position(rest.row, rest.col): rest
            for rest in long_rests
        }

        for rest in long_rests:
            remaining_ratio = rest.remaining_ratio(current_time)
            fill_height = int(round(cell_h * remaining_ratio))
            if fill_height <= 0:
                continue
            board_canvas.draw_rectangle(
                rest.col * cell_w,
                rest.row * cell_h + cell_h - fill_height,
                cell_w,
                fill_height,
                LONG_REST_BACKGROUND_COLOR,
                thickness=-1,
            )

        for jump in jumps:
            board_canvas.draw_rectangle(
                jump.col * cell_w,
                jump.row * cell_h,
                cell_w,
                cell_h,
                AIRBORNE_BACKGROUND_COLOR,
                thickness=-1,
            )

        for row, tokens in enumerate(snapshot.token_grid):
            for col, token in enumerate(tokens):
                if token == constants.EMPTY_CELL or len(token) != 2:
                    continue
                cell = Position(row, col)
                if cell in moving_sources or cell in jumping_cells:
                    continue
                rest = rests_by_cell.get(cell)
                if rest is not None:
                    elapsed_ms = max(0, current_time - rest.start_time)
                    piece_img = self._piece_sprite(
                        token,
                        state_name="long_rest",
                        elapsed_ms=elapsed_ms,
                    )
                    x, y = col * cell_w, row * cell_h
                else:
                    piece_img = self._piece_sprite(
                        token,
                        state_name="idle",
                        elapsed_ms=visual_time_ms,
                    )
                    x, y = idle_pixel_position(
                        row,
                        col,
                        visual_time_ms,
                        cell_size,
                    )
                piece_img.draw_on_clipped(
                    board_canvas,
                    int(round(x)),
                    int(round(y)),
                )

        dot_radius = max(4, cell_size // 9)
        for destination in legal_destinations:
            if (
                0 <= destination.row < snapshot.board_height
                and 0 <= destination.col < snapshot.board_width
            ):
                board_canvas.draw_circle(
                    destination.col * cell_w + cell_w // 2,
                    destination.row * cell_h + cell_h // 2,
                    dot_radius,
                    LEGAL_MOVE_DOT_COLOR,
                )

        selected = snapshot.selected_cell
        if selected is not None and (
            0 <= selected.row < snapshot.board_height
            and 0 <= selected.col < snapshot.board_width
        ):
            board_canvas.draw_rectangle(
                selected.col * cell_w,
                selected.row * cell_h,
                cell_w,
                cell_h,
                SELECTED_BORDER_COLOR,
                thickness=max(2, cell_size // 20),
            )

        for motion in motions:
            x, y = motion_pixel_position(motion, current_time, cell_size)
            elapsed_ms = int(
                motion_progress(motion, current_time) * motion.duration
            )
            piece_img = self._piece_sprite(
                motion.piece_token,
                state_name="move",
                elapsed_ms=elapsed_ms,
            )
            piece_img.draw_on_clipped(
                board_canvas,
                int(round(x)),
                int(round(y)),
            )

        for jump in jumps:
            x, y = jump_pixel_position(jump, current_time, cell_size)
            elapsed_ms = int(
                jump_progress(jump, current_time) * jump.duration
            )
            piece_img = self._piece_sprite(
                jump.piece_token,
                state_name="jump",
                elapsed_ms=elapsed_ms,
            )
            piece_img.draw_on_clipped(
                board_canvas,
                int(round(x)),
                int(round(y)),
            )

        if snapshot.game_over:
            canvas_width, canvas_height = canvas_size
            banner_height = max(cell_size, canvas_height // 4)
            banner_y = (canvas_height - banner_height) // 2
            board_canvas.draw_rectangle(
                0,
                banner_y,
                canvas_width,
                banner_height,
                GAME_OVER_BACKGROUND_COLOR,
                thickness=-1,
            )
            board_canvas.put_centered_text(
                "Game Over",
                canvas_width // 2,
                canvas_height // 2,
                font_size=max(0.5, cell_size / 45.0),
                color=GAME_OVER_TEXT_COLOR,
                thickness=max(1, cell_size // 25),
            )

        return board_canvas
