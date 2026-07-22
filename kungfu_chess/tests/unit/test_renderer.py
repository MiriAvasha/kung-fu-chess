import json

import cv2
import numpy as np
import pytest

from engine.results import GameSnapshot
from img import Img
from model.position import Position
from view.renderer import LEGAL_MOVE_DOT_COLOR, SELECTED_BORDER_COLOR, Renderer


def _write_image(path, width, height, color):
    image = np.zeros((height, width, 4), dtype=np.uint8)
    image[:, :] = color
    assert cv2.imwrite(str(path), image)


def _write_idle_piece(pieces_root, token):
    idle_path = pieces_root / token / 'states' / 'idle'
    sprites_path = idle_path / 'sprites'
    sprites_path.mkdir(parents=True)
    (idle_path / 'config.json').write_text(
        json.dumps({
            'physics': {},
            'graphics': {'frames_per_sec': 1, 'is_loop': True},
        }),
        encoding='utf-8',
    )
    _write_image(sprites_path / '1.png', 10, 10, (10, 20, 30, 255))


class TestRenderer:
    def test_render_uses_snapshot_dimensions_and_tokens(self, tmp_path):
        board_path = tmp_path / 'board.png'
        pieces_root = tmp_path / 'pieces'
        _write_image(board_path, 37, 31, (0, 0, 0, 255))
        _write_idle_piece(pieces_root, 'wK')

        renderer = Renderer(str(board_path), str(pieces_root), cell_size=10)
        snapshot = GameSnapshot(
            2,
            2,
            [['wK', '.'], ['.', '.']],
            game_over=False,
        )

        result = renderer.render(snapshot)

        assert isinstance(result, Img)
        assert result.img.shape == (20, 20, 4)
        assert tuple(result.img[5, 5]) == (10, 20, 30, 255)
        assert tuple(result.img[15, 15]) == (0, 0, 0, 255)

    def test_render_marks_selected_cell(self, tmp_path):
        board_path = tmp_path / 'board.png'
        _write_image(board_path, 20, 20, (0, 0, 0, 255))
        renderer = Renderer(
            str(board_path),
            str(tmp_path / 'pieces'),
            cell_size=10,
        )
        snapshot = GameSnapshot(
            2,
            2,
            [['.', '.'], ['.', '.']],
            game_over=False,
            selected_cell=Position(0, 1),
        )

        result = renderer.render(snapshot)

        assert tuple(result.img[0, 10]) == SELECTED_BORDER_COLOR
        assert tuple(result.img[5, 15]) == (0, 0, 0, 255)

    def test_render_marks_legal_destinations_with_center_dots(self, tmp_path):
        board_path = tmp_path / 'board.png'
        _write_image(board_path, 20, 20, (0, 0, 0, 255))
        renderer = Renderer(
            str(board_path),
            str(tmp_path / 'pieces'),
            cell_size=10,
        )
        snapshot = GameSnapshot(
            2,
            2,
            [['.', '.'], ['.', '.']],
            game_over=False,
        )

        result = renderer.render(snapshot, {Position(1, 0)})

        assert tuple(result.img[15, 5]) == LEGAL_MOVE_DOT_COLOR
        assert tuple(result.img[5, 15]) == (0, 0, 0, 255)

    def test_render_rejects_empty_board_dimensions(self, tmp_path):
        board_path = tmp_path / 'board.png'
        _write_image(board_path, 20, 20, (0, 0, 0, 255))
        renderer = Renderer(str(board_path), str(tmp_path / 'pieces'))
        snapshot = GameSnapshot(0, 0, [], game_over=False)

        with pytest.raises(ValueError, match='dimensions must be positive'):
            renderer.render(snapshot)
