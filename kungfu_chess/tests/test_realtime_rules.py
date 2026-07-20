import constants
from model.position import Position
from tests.conftest import make_engine


class TestCaptures:
    def test_later_arriver_captures_idle_enemy(self):
        engine = make_engine([
            ['wR', '.', 'bN'],
        ])
        engine.request_move(Position(0, 0), Position(0, 2))
        engine.wait(2000)
        assert engine.game_state.board.piece_at(Position(0, 2)).token == 'wR'
        assert len(engine.game_state.board.all_pieces()) == 1

    def test_later_eats_earlier_on_same_destination(self):
        # Two enemies race to same empty square; later arrival wins the square.
        engine = make_engine([
            ['wR', '.', '.', 'bR'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        # White needs 2 cells (2000ms), black needs 1 cell from col3? wait black at (0,3) to (0,2) is 1 cell
        # Better: both to (0,2)
        # wR at (0,0)->(0,2) duration 2000; bR at (2,2)->(0,2) duration 2000 but start later
        engine = make_engine([
            ['wR', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bR'],
        ])
        engine.request_move(Position(0, 0), Position(0, 2))  # arrives at 2000
        engine.wait(500)
        engine.request_move(Position(2, 2), Position(0, 2))  # arrives at 500+2000=2500
        engine.wait(2500)
        assert engine.game_state.board.piece_at(Position(0, 2)).token == 'bR'
        assert engine.game_state.board.piece_at(Position(0, 0)) is None
        assert engine.game_state.board.piece_at(Position(2, 2)) is None

    def test_head_on_swap_later_eats_earlier(self):
        engine = make_engine([
            ['wR', '.', 'bR'],
        ])
        # Both travel 2 cells → same duration; white starts first (lower order) → earlier.
        engine.request_move(Position(0, 0), Position(0, 2))
        engine.request_move(Position(0, 2), Position(0, 0))
        engine.wait(2000)
        # Later (black, higher order on tie) eats white on white's square (0,0)
        # Looking at arbiter: earlier cancelled, later captures them on their square.
        # White order=1 arrives 2000, black order=2 arrives 2000 → white earlier → cancelled
        # Black applies and captures white at (0,0) which is black's destination.
        assert engine.game_state.board.piece_at(Position(0, 0)).token == 'bR'
        assert engine.game_state.board.piece_at(Position(0, 2)) is None

    def test_same_color_never_captures_on_destination(self):
        # Ally arrives first on the square; later ally must stop before it.
        engine = make_engine([
            ['wR', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'wR'],
        ])
        engine.request_move(Position(0, 0), Position(0, 2))  # arrives t=2000
        engine.wait(500)
        engine.request_move(Position(2, 2), Position(0, 2))  # arrives t=2500
        engine.wait(2500)
        assert engine.game_state.board.piece_at(Position(0, 2)).token == 'wR'
        assert engine.game_state.board.piece_at(Position(1, 2)).token == 'wR'


class TestSameColorPathBlocks:
    def test_later_ally_stops_before_shared_cell(self):
        # Two white rooks approaching same corridor cell.
        engine = make_engine([
            ['wR', '.', '.', '.', 'wR'],
        ])
        engine.request_move(Position(0, 0), Position(0, 3))  # path 0,1,2,3
        engine.request_move(Position(0, 4), Position(0, 1))  # path 4,3,2,1 — shares 1,2,3
        engine.wait(4000)
        pieces = {(p.cell.row, p.cell.col): p.token for p in engine.game_state.board.all_pieces()}
        # Both should survive (same color)
        assert list(pieces.values()).count('wR') == 2
        # Later mover should not land on / through the earlier one's path in a capturing way
        assert (0, 3) in pieces or (0, 2) in pieces or (0, 1) in pieces

    def test_static_ally_on_path_truncates(self):
        # Long rook path shares a cell with a shorter ally move that arrives first → truncate long.
        engine = make_engine([
            ['wR', '.', '.', '.', '.'],
            ['.', '.', 'wR', '.', '.'],
        ])
        assert engine.request_move(Position(0, 0), Position(0, 4)).is_accepted
        assert engine.request_move(Position(1, 2), Position(0, 2)).is_accepted
        engine.wait(5000)
        assert engine.game_state.board.piece_at(Position(0, 2)).token == 'wR'
        assert engine.game_state.board.piece_at(Position(0, 1)).token == 'wR'
        assert engine.game_state.board.piece_at(Position(0, 4)) is None


class TestAirborneJump:
    def test_airborne_defender_eats_attacker(self):
        # Attacker must arrive while jump is still active (JUMP_DURATION=1000).
        engine = make_engine([
            ['wR', 'bN'],
        ])
        assert engine.request_jump(Position(0, 1)).is_accepted
        engine.request_move(Position(0, 0), Position(0, 1))
        engine.wait(1000)
        assert engine.game_state.board.piece_at(Position(0, 1)).token == 'bN'
        assert engine.game_state.board.piece_at(Position(0, 0)) is None

    def test_king_attacker_eaten_by_airborne_ends_game(self):
        engine = make_engine([
            ['wK', 'bN'],
        ])
        engine.request_jump(Position(0, 1))
        engine.request_move(Position(0, 0), Position(0, 1))
        engine.wait(1000)
        assert engine.game_state.game_over is True
        assert engine.game_state.board.piece_at(Position(0, 0)) is None
        assert engine.game_state.board.piece_at(Position(0, 1)).token == 'bN'


class TestGameOverAndPromotion:
    def test_capturing_king_ends_game(self):
        engine = make_engine([
            ['wR', '.', 'bK'],
        ])
        engine.request_move(Position(0, 0), Position(0, 2))
        engine.wait(2000)
        assert engine.game_state.game_over is True
        assert engine.game_state.board.piece_at(Position(0, 2)).token == 'wR'

    def test_white_pawn_promotes_to_queen(self):
        engine = make_engine([
            ['.', '.', '.'],
            ['wP', '.', '.'],
            ['.', '.', '.'],
        ])
        # Pawn at row1 needs to go to row0 — but from row1 white pawn forward is -1 → row0
        engine.request_move(Position(1, 0), Position(0, 0))
        engine.wait(1000)
        assert engine.game_state.board.piece_at(Position(0, 0)).token == 'wQ'

    def test_black_pawn_promotes_to_queen(self):
        engine = make_engine([
            ['.', '.', '.'],
            ['.', '.', '.'],
            ['bP', '.', '.'],
        ])
        engine.request_move(Position(2, 0), Position(2, 0))  # same square illegal
        # Put black pawn at row height-2 = 1 for height 3? black promotes at height-1=2
        engine = make_engine([
            ['.'],
            ['bP'],
            ['.'],
        ])
        # black at (1,0) forward +1 → (2,0) last rank
        engine.request_move(Position(1, 0), Position(2, 0))
        engine.wait(1000)
        assert engine.game_state.board.piece_at(Position(2, 0)).token == 'bQ'
