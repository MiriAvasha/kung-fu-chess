import constants
from model.position import Position


class BoardMapper:
    def __init__(self, board_width: int, board_height: int):
        self.board_width = board_width
        self.board_height = board_height

    def pixel_to_cell(self, x: int, y: int) -> Position:
        return Position(y // constants.CELL_SIZE, x // constants.CELL_SIZE)

    def is_inside_board(self, position: Position) -> bool:
        return 0 <= position.row < self.board_height and 0 <= position.col < self.board_width
