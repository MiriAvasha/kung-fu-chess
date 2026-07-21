import os

from engine.game_engine import GameEngine
from input.controller import Controller
from model.board import board_from_token_rows
from model.game_state import GameState
from realtime.real_time_arbiter import RealTimeArbiter
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

    def render_current_state():
        snapshot = engine.snapshot(controller.selected_cell)
        return renderer.render(snapshot)

    def handle_click(x: int, y: int):
        controller.click(x, y)
        return render_current_state()

    image_view.run(render_current_state(), handle_click)


if __name__ == '__main__':
    main()
