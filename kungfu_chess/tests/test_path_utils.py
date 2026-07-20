from model.position import Position
from rules.path_utils import (
    earlier_stop_along_path,
    is_earlier_arrival,
    last_square_before,
    path_cells,
    shared_path_cells,
    time_to_leave_cell,
    time_to_reach_cell,
)


class TestPathUtils:
    def test_rook_path_includes_intermediates(self):
        path = path_cells(Position(0, 0), Position(0, 3))
        assert path == [Position(0, 0), Position(0, 1), Position(0, 2), Position(0, 3)]

    def test_bishop_path(self):
        path = path_cells(Position(2, 2), Position(0, 0))
        assert path == [Position(2, 2), Position(1, 1), Position(0, 0)]

    def test_knight_leap_has_no_intermediates(self):
        path = path_cells(Position(0, 0), Position(2, 1))
        assert path == [Position(0, 0), Position(2, 1)]

    def test_last_square_before_collision(self):
        stop = last_square_before(Position(0, 0), Position(0, 4), Position(0, 3))
        assert stop == Position(0, 2)

    def test_time_to_reach_scales_along_path(self):
        t = time_to_reach_cell(0, 3000, Position(0, 0), Position(0, 3), Position(0, 1))
        assert t == 1000

    def test_time_to_leave_destination_is_none(self):
        leave = time_to_leave_cell(0, 2000, Position(0, 0), Position(0, 2), Position(0, 2))
        assert leave is None

    def test_shared_path_cells(self):
        shared = shared_path_cells(
            Position(0, 0), Position(0, 4),
            Position(2, 2), Position(0, 2),
        )
        assert Position(0, 2) in shared

    def test_earlier_arrival_uses_order_on_tie(self):
        assert is_earlier_arrival(100, 1, 100, 2)
        assert not is_earlier_arrival(100, 2, 100, 1)
        assert is_earlier_arrival(50, 9, 100, 1)

    def test_earlier_stop_along_path_picks_closer(self):
        better = earlier_stop_along_path(
            Position(0, 0), Position(0, 5),
            Position(0, 4), Position(0, 2),
        )
        assert better == Position(0, 2)
