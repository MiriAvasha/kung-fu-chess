from board_io.board_parser import BoardParser
from model.position import Position


class TestBoardParser:
    def test_parses_rows_into_game_state(self):
        parser = BoardParser()
        state = parser.add_row('wR . bK')
        state = parser.add_row('. wP .')
        assert state.board.width == 3
        assert state.board.height == 2
        assert state.board.piece_at(Position(0, 0)).token == 'wR'
        assert state.board.piece_at(Position(1, 1)).token == 'wP'
        assert state.board.piece_at(Position(0, 2)).token == 'bK'
        assert state.game_over is False

    def test_single_row_board(self):
        parser = BoardParser()
        state = parser.add_row('wK . .')
        assert state.board.height == 1
        assert state.board.width == 3
        assert state.board.to_token_grid() == [['wK', '.', '.']]
