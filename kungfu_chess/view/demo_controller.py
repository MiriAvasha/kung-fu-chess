from assets.piece_loader import PieceAssetLoader
from model.board import board_from_token_rows
from model.position import Position
from rules.piece_rules import PIECE_RULES
from rules.promotion import DEFAULT_PROMOTION_SERVICE
from states.piece_state_machine import PieceStateMachine, STATE_IDLE
from view.board_view import BoardView

import constants


DEMO_BOARD = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
]


class DemoController:
    def __init__(self, pieces_root: str, cell_size: int = constants.CELL_SIZE):
        self.cell_size = cell_size
        self.pieces_root = pieces_root
        self.board = board_from_token_rows(DEMO_BOARD)
        self.loader = PieceAssetLoader(pieces_root, cell_size)
        self.view = BoardView(cell_size)
        self.promotion = DEFAULT_PROMOTION_SERVICE
        self.machines = {}
        self.selected_cell = None
        self.legal_destinations = set()
        self.game_over = False

        for piece in self.board.all_pieces():
            self._create_machine(piece)

    def _create_machine(self, piece):
        assets = self.loader.load(piece.color, piece.kind)
        machine = PieceStateMachine(assets)
        machine.place_at_cell(piece.cell.row, piece.cell.col, self.cell_size)
        self.machines[piece.id] = machine
        return machine

    def _machine_for_cell(self, cell: Position):
        piece = self.board.piece_at(cell)
        if piece is None:
            return None, None
        return piece, self.machines.get(piece.id)

    def click(self, x: int, y: int):
        if self.game_over:
            return

        cell = Position(y // self.cell_size, x // self.cell_size)
        if not self.board.is_inside(cell):
            self.selected_cell = None
            self.legal_destinations = set()
            return

        if self.selected_cell is not None:
            if cell in self.legal_destinations:
                self._start_move(self.selected_cell, cell)
                self.selected_cell = None
                self.legal_destinations = set()
                return

            selected_piece = self.board.piece_at(self.selected_cell)
            clicked_piece = self.board.piece_at(cell)
            if (
                clicked_piece is not None
                and selected_piece is not None
                and clicked_piece.color == selected_piece.color
            ):
                self._select(cell)
                return

            self.selected_cell = None
            self.legal_destinations = set()
            if clicked_piece is not None:
                self._select(cell)
            return

        self._select(cell)

    def jump_selected(self):
        if self.game_over or self.selected_cell is None:
            return
        piece, machine = self._machine_for_cell(self.selected_cell)
        if piece is None or machine is None or not machine.is_idle:
            return

        source = self.selected_cell

        def on_landed(_cell):
            piece.state = STATE_IDLE

        piece.state = 'jumping'
        machine.start_jump(source, self.cell_size, on_arrived=on_landed)
        self.selected_cell = None
        self.legal_destinations = set()

    def _select(self, cell: Position):
        piece, machine = self._machine_for_cell(cell)
        if piece is None or machine is None or not machine.is_idle:
            self.selected_cell = None
            self.legal_destinations = set()
            return
        self.selected_cell = cell
        rule = PIECE_RULES.get(piece.kind)
        if rule is None:
            self.legal_destinations = set()
            return
        self.legal_destinations = rule.legal_destinations(self.board, piece)

    def _start_move(self, source: Position, destination: Position):
        piece, machine = self._machine_for_cell(source)
        if piece is None or machine is None or not machine.is_idle:
            return

        def on_arrived(dest: Position):
            captured = self.board.piece_at(dest)
            if captured is not None:
                self.board.remove_piece(dest)
                if captured.id in self.machines:
                    del self.machines[captured.id]
                if captured.kind == 'K':
                    self.game_over = True

            new_kind = self.promotion.resolve(self.board, piece, dest)
            self.board.move_piece(source, dest, new_kind)
            piece.state = STATE_IDLE
            if new_kind is not None:
                # Same machine continues rest; only sprites/config switch to new kind.
                machine.assets = self.loader.load(piece.color, piece.kind)
            machine.place_at_cell(dest.row, dest.col, self.cell_size)

        piece.state = 'moving'
        machine.start_move(source, destination, self.cell_size, on_arrived=on_arrived)

    def tick(self, dt_ms: int):
        if self.game_over:
            return
        for machine in list(self.machines.values()):
            machine.tick(dt_ms, self.cell_size)

    def draw(self, surface):
        self.view.draw(
            surface,
            self.board,
            self.machines,
            selected_cell=self.selected_cell,
            legal_destinations=self.legal_destinations,
            game_over=self.game_over,
        )
