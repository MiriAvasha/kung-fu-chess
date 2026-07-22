import os

from engine.game_engine import GameEngine
from input.controller import Controller
from model.board import board_from_token_rows
from model.game_state import GameState
from realtime.real_time_arbiter import RealTimeArbiter
from rules.piece_rules import PIECE_RULES
from rules.rule_engine import RuleEngine
from view.image_view import ImageView
from view.renderer import Renderer


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


def build_engine() -> GameEngine:
    game_state = GameState(board_from_token_rows(STARTING_BOARD))
    return GameEngine(game_state, RuleEngine(), RealTimeArbiter())


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    board_path = os.path.join(base_dir, 'assets', 'board.png')
    pieces_path = os.path.join(base_dir, 'assets', 'pieces')

    engine = build_engine()
    renderer = Renderer(board_path, pieces_path)
    controller = Controller(engine, cell_size=renderer.cell_size)
    image_view = ImageView()
    visual_time_ms = [0]

    def render_current_state():
        snapshot = engine.snapshot(controller.selected_cell)
        legal_destinations = set()
        if controller.selected_cell is not None:
            piece = engine.game_state.board.piece_at(controller.selected_cell)
            if piece is not None:
                rule = PIECE_RULES.get(piece.kind)
                if rule is not None:
                    legal_destinations = rule.legal_destinations(
                        engine.game_state.board,
                        piece,
                    )
        return renderer.render(
            snapshot,
            legal_destinations,
            active_motions=engine.arbiter.active_motions.values(),
            active_jumps=engine.arbiter.active_jumps.values(),
            current_time=engine.arbiter.current_time,
            visual_time_ms=visual_time_ms[0],
        )

    def handle_click(x: int, y: int):
        controller.click(x, y)

    def advance_animation(elapsed_ms: int):
        visual_time_ms[0] += elapsed_ms
        has_timed_action = (
            engine.arbiter.has_any_active_motion()
            or bool(engine.arbiter.active_jumps)
        )
        if elapsed_ms > 0 and has_timed_action:
            engine.wait(elapsed_ms)

    def is_animating():
        return not engine.game_state.game_over

    image_view.run(
        render_current_state,
        handle_click,
        advance_animation,
        is_animating,
    )


if __name__ == '__main__':
    main()
