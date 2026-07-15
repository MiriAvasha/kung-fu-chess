from assets.piece_loader import PieceAssetLoader
from model.board import board_from_token_rows
from model.position import Position
from rules.path_utils import last_square_before, last_squares_before_head_on
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
        self.active_moves = {}
        self._move_order = 0
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

    def _eliminate(self, piece, cell: Position):
        """Remove a piece from the board and cancel any in-flight move/animation."""
        self.active_moves.pop(piece.id, None)
        if self.board.piece_at(cell) is piece:
            self.board.remove_piece(cell)
        machine = self.machines.pop(piece.id, None)
        if machine is not None:
            machine._on_arrived = None
        if piece.kind == 'K':
            self.game_over = True

    def _find_mutual_swap(self, piece_id, source: Position, dest: Position):
        for other_id, move in self.active_moves.items():
            if other_id == piece_id:
                continue
            if move['source'] == dest and move['dest'] == source:
                return move
        return None

    def _find_same_destination_ally(self, piece_id, dest: Position, color: str):
        for other_id, move in self.active_moves.items():
            if other_id == piece_id:
                continue
            if move['dest'] == dest and move['piece'].color == color:
                return move
        return None

    def _settle_before_collision(self, piece, from_cell: Position, stop_cell: Position, abort_animation: bool = True):
        """Same-color collision: stay on closest square reached before they met."""
        self.active_moves.pop(piece.id, None)
        landed = from_cell
        if stop_cell != from_cell and self.board.piece_at(from_cell) is piece:
            if self.board.piece_at(stop_cell) is None:
                new_kind = self.promotion.resolve(self.board, piece, stop_cell)
                self.board.move_piece(from_cell, stop_cell, new_kind)
                if new_kind is not None:
                    machine = self.machines.get(piece.id)
                    if machine is not None:
                        machine.assets = self.loader.load(piece.color, piece.kind)
                landed = stop_cell
            else:
                stop_cell = from_cell
        else:
            stop_cell = landed
        piece.state = STATE_IDLE
        if abort_animation:
            machine = self.machines.get(piece.id)
            if machine is not None:
                machine.abort_to_cell(stop_cell, self.cell_size)
        return stop_cell

    def click(self, x: int, y: int):
        if self.game_over:
            return

        cell = Position(y // self.cell_size, x // self.cell_size)
        if not self.board.is_inside(cell):
            self.selected_cell = None
            self.legal_destinations = set()
            return

        if self.selected_cell is not None:
            # Second click on the same square = jump (stay on cell, airborne).
            if cell == self.selected_cell:
                self.jump_selected()
                return

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

        self._move_order += 1
        order = self._move_order
        self.active_moves[piece.id] = {
            'piece': piece,
            'source': source,
            'dest': destination,
            'order': order,
        }

        def on_arrived(dest: Position):
            move = self.active_moves.pop(piece.id, None)
            if move is None or piece.id not in self.machines:
                # Already cancelled / captured by an earlier opponent.
                return source

            swap = self._find_mutual_swap(piece.id, source, dest)

            # Same-color head-on: each stops on closest square reached before meeting.
            if swap is not None and swap['piece'].color == piece.color:
                stop_a, stop_b = last_squares_before_head_on(
                    source, dest, swap['source'], swap['dest']
                )
                self._settle_before_collision(swap['piece'], swap['source'], stop_b)
                return self._settle_before_collision(
                    piece, source, stop_a, abort_animation=False
                )

            same_dest_ally = self._find_same_destination_ally(piece.id, dest, piece.color)
            if same_dest_ally is not None:
                stop_self = last_square_before(source, dest, dest)
                stop_other = last_square_before(
                    same_dest_ally['source'], same_dest_ally['dest'], dest
                )
                self._settle_before_collision(
                    same_dest_ally['piece'], same_dest_ally['source'], stop_other
                )
                return self._settle_before_collision(
                    piece, source, stop_self, abort_animation=False
                )

            # Opposite-color head-on: first to leave eats the other.
            if swap is not None and swap['piece'].color != piece.color:
                if swap['order'] < order:
                    # Opponent left first — they eat us.
                    self._eliminate(piece, source)
                    return source
                # We left first — eat them, then land on their square.
                self._eliminate(swap['piece'], swap['source'])

            target = self.board.piece_at(dest)

            # Ally on destination: stop on closest square before that meeting cell.
            if target is not None and target.color == piece.color:
                stop = last_square_before(source, dest, dest)
                return self._settle_before_collision(
                    piece, source, stop, abort_animation=False
                )

            if target is not None and target.color != piece.color:
                target_machine = self.machines.get(target.id)
                # Airborne jumper eats the attacker instead of being captured.
                if target_machine is not None and target_machine.is_jumping:
                    self._eliminate(piece, source)
                    return source

                self._eliminate(target, dest)

            if piece.id not in self.machines:
                return source

            new_kind = self.promotion.resolve(self.board, piece, dest)
            self.board.move_piece(source, dest, new_kind)
            piece.state = STATE_IDLE
            if new_kind is not None:
                machine.assets = self.loader.load(piece.color, piece.kind)
            return None

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
