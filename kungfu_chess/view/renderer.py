import os
import sys
from typing import Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants
from assets.piece_loader import PieceAssetLoader
from engine.results import GameSnapshot
from img import Img


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

        if pieces_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pieces_path = os.path.join(base_dir, 'assets', 'pieces')
        self.piece_loader = PieceAssetLoader(pieces_path, cell_size=cell_size)

    def _cell_metrics(
        self,
        snapshot: GameSnapshot,
        board_canvas: Img,
    ) -> Tuple[int, int, int]:
        if snapshot.board_width <= 0 or snapshot.board_height <= 0:
            raise ValueError('Snapshot board dimensions must be positive')

        height, width = board_canvas.img.shape[:2]
        cell_h = height // snapshot.board_height
        cell_w = width // snapshot.board_width
        cell_size = min(cell_h, cell_w)
        return cell_w, cell_h, cell_size

    def _piece_sprite(self, token: str) -> Img:
        color, kind = token[0], token[1]
        piece_assets = self.piece_loader.load(color, kind)
        idle_state = piece_assets.get_state("idle")
        if idle_state is None or not idle_state.sprites:
            raise FileNotFoundError(
                f"No idle sprite for {token}. "
                f"Available states: {sorted(piece_assets.states.keys())}"
            )
        return idle_state.sprites[0]

    def render(self, snapshot: GameSnapshot) -> Img:
        board_canvas = Img().read(self.board_image_path)
        cell_w, cell_h, cell_size = self._cell_metrics(snapshot, board_canvas)
        self.piece_loader.set_cell_size(cell_size)

        for row, tokens in enumerate(snapshot.token_grid):
            for col, token in enumerate(tokens):
                if token == constants.EMPTY_CELL or len(token) != 2:
                    continue
                piece_img = self._piece_sprite(token)
                x = col * cell_w
                y = row * cell_h
                piece_img.draw_on(board_canvas, x, y)

        return board_canvas
