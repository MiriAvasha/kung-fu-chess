from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState


def sync_game_state_from_grid(game_state: GameState, grid: List[List[str]]):
    game_state.board = Board.from_token_rows(grid)


def sync_grid_from_game_state(grid: list, game_state: GameState):
    token_grid = game_state.board.to_token_grid()
    grid.clear()
    grid.extend(token_grid)
