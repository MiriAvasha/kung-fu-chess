from kungfu_chess import constants
from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.model.position import Position


class Controller:
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.selected_cell = None

    def _mapper(self) -> BoardMapper:
        board = self.engine.game_state.board
        return BoardMapper(board.width, board.height)

    def click(self, x: int, y: int):
        if self.engine.game_state.game_over:
            return

        self.engine.arbiter.complete_pending(self.engine.game_state)
        if self.engine.game_state.game_over:
            return

        mapper = self._mapper()
        cell = mapper.pixel_to_cell(x, y)

        if self.selected_cell is not None and not mapper.is_inside_board(cell):
            self.selected_cell = None
            return

        if not mapper.is_inside_board(cell):
            return

        board = self.engine.game_state.board
        clicked_piece = board.piece_at(cell)

        if self.selected_cell is not None:
            source = self.selected_cell
            source_piece = board.piece_at(source)
            if source_piece is None:
                self.selected_cell = None
                return

            result = self.engine.request_move(source, cell)
            if result.is_accepted:
                self.selected_cell = None
            elif clicked_piece is not None and clicked_piece.color == source_piece.color:
                self.selected_cell = cell
            else:
                self.selected_cell = None
        elif clicked_piece is not None:
            if self.engine.arbiter.has_active_motion_from(cell.row, cell.col):
                return
            self.selected_cell = cell

    def jump(self, x: int, y: int):
        mapper = self._mapper()
        cell = mapper.pixel_to_cell(x, y)
        self.engine.request_jump(cell)
