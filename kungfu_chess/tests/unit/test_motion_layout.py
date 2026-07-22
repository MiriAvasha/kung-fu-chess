from model.position import Position
from realtime.motion import Motion
from view.motion_layout import (
    motion_pixel_position,
    motion_progress,
    motion_source_cells,
)


def _motion():
    return Motion(
        piece_id=1,
        piece_token='wR',
        from_row=1,
        from_col=0,
        to_row=1,
        to_col=2,
        start_time=100,
        duration=1000,
        order=1,
    )


def test_motion_progress_is_clamped_to_motion_duration():
    motion = _motion()

    assert motion_progress(motion, 0) == 0.0
    assert motion_progress(motion, 600) == 0.5
    assert motion_progress(motion, 1200) == 1.0


def test_motion_pixel_position_interpolates_between_cells():
    motion = _motion()

    assert motion_pixel_position(motion, 600, cell_size=100) == (100.0, 100.0)


def test_motion_source_cells_returns_original_board_cells():
    motion = _motion()

    assert motion_source_cells([motion]) == {Position(1, 0)}
