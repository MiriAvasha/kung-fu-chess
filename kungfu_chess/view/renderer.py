import os
import sys
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants
from img import Img
from assets.piece_loader import PieceAssetLoader

COLOR_ALIASES = {
    'white': 'w',
    'black': 'b',
    'w': 'w',
    'b': 'b',
}

KIND_ALIASES = {
    'pawn': 'P',
    'rook': 'R',
    'knight': 'N',
    'bishop': 'B',
    'queen': 'Q',
    'king': 'K',
    'p': 'P',
    'r': 'R',
    'n': 'N',
    'b': 'B',
    'q': 'Q',
    'k': 'K',
}


STARTING_BOARD = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
]


class Renderer:
    def __init__(self, board_image_path: str = "board.png", cell_size: int = 100):
        self.board_image_path = board_image_path
        self.cell_size = cell_size

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pieces_path = os.path.join(base_dir, "assets", "pieces")
        self.piece_loader = PieceAssetLoader(pieces_path, cell_size=cell_size)

    @staticmethod
    def _normalize_piece(color: str, kind: str) -> Tuple[str, str]:
        color_key = color.lower()
        kind_key = kind.lower()
        normalized_color = COLOR_ALIASES.get(color_key, color)
        normalized_kind = KIND_ALIASES.get(kind_key, kind.upper() if len(kind) == 1 else kind)
        return normalized_color, normalized_kind

    def render_board_only(self):
        board_canvas = Img().read(self.board_image_path)
        board_canvas.show()

    def _cell_metrics(self, board_canvas: Img) -> Tuple[int, int, int]:
        height, width = board_canvas.img.shape[:2]
        rows = len(STARTING_BOARD)
        cols = len(STARTING_BOARD[0])
        cell_h = height // rows
        cell_w = width // cols
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

    def render_board_with_grid(self, token_grid: List[List[str]]):
        board_canvas = Img().read(self.board_image_path)
        cell_w, cell_h, cell_size = self._cell_metrics(board_canvas)
        self.piece_loader.set_cell_size(cell_size)

        for row, tokens in enumerate(token_grid):
            for col, token in enumerate(tokens):
                if token == constants.EMPTY_CELL or len(token) != 2:
                    continue
                piece_img = self._piece_sprite(token)
                x = col * cell_w
                y = row * cell_h
                piece_img.draw_on(board_canvas, x, y)

        board_canvas.show()

    def render_starting_board(self):
        self.render_board_with_grid(STARTING_BOARD)

    def render_board_with_piece(self, piece_color: str, piece_kind: str, x: int, y: int):
        board_canvas = Img().read(self.board_image_path)

        color, kind = self._normalize_piece(piece_color, piece_kind)
        piece_assets = self.piece_loader.load(color, kind)

        idle_state = piece_assets.get_state("idle")
        if idle_state is None or not idle_state.sprites:
            raise FileNotFoundError(
                f"No idle sprite for {color}{kind}. "
                f"Available states: {sorted(piece_assets.states.keys())}"
            )

        piece_img = idle_state.sprites[0]
        piece_img.draw_on(board_canvas, x, y)
        board_canvas.show()


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    board_path = os.path.join(base_dir, "assets", "board.png")

    renderer = Renderer(board_image_path=board_path)
    renderer.render_starting_board()
