from assets.piece_loader import PieceAssetLoader
from model.board import board_from_token_rows
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

MIN_CELL_SIZE = 60
MAX_CELL_SIZE = 120
CELL_SIZE_STEP = 10


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
        self._time_ms = 0
        self.selected_cell = None
        self.legal_destinations = set()
        self.game_over = False

        for piece in self.board.all_pieces():
            self._create_machine(piece)

    def window_size(self, help_h: int = 108):
        return (
            self.board.width * self.cell_size,
            self.board.height * self.cell_size + help_h,
        )

    def set_cell_size(self, cell_size: int) -> bool:
        """Zoom board cells. Returns True if size actually changed."""
        cell_size = max(MIN_CELL_SIZE, min(MAX_CELL_SIZE, cell_size))
        cell_size = (cell_size // CELL_SIZE_STEP) * CELL_SIZE_STEP
        if cell_size == self.cell_size:
            return False

        self.cell_size = cell_size
        self.loader.set_cell_size(cell_size)
        self.view.cell_size = cell_size
        self.view._tint_cache.clear()

        for piece in self.board.all_pieces():
            machine = self.machines.get(piece.id)
            if machine is None:
                continue
            machine.assets = self.loader.load(piece.color, piece.kind)
            # Recalculate pixels with the new cell size (keeps move/jump progress).
            machine.tick(0, self.cell_size)
            if machine.is_idle or machine.is_resting:
                machine.place_at_cell(piece.cell.row, piece.cell.col, self.cell_size)
        return True

    def shrink_board(self) -> bool:
        return self.set_cell_size(self.cell_size - CELL_SIZE_STEP)

    def grow_board(self) -> bool:
        return self.set_cell_size(self.cell_size + CELL_SIZE_STEP)

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

    def _settle_before_collision(self, piece, from_cell: Position, stop_cell: Position, abort_animation: bool = True):
        """Same-color: stay on closest square reached before the meeting cell."""
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

    def _truncate_move(self, move, stop: Position):
        machine = self.machines.get(move['piece'].id)
        if machine is None:
            return
        source = move['source']
        original = move['original_dest']
        path = path_cells(source, original)
        try:
            stop_index = path.index(stop)
        except ValueError:
            return
        steps = len(path) - 1
        if steps <= 0:
            return
        move['dest'] = stop
        machine.to_pos = stop
        machine.duration_ms = int(round(move['original_duration'] * stop_index / float(steps)))

    def _resolve_same_color_path_blocks(self):
        moves = list(self.active_moves.values())
        for i in range(len(moves)):
            for j in range(i + 1, len(moves)):
                a = moves[i]
                b = moves[j]
                if a['piece'].color != b['piece'].color:
                    continue
                for cell in shared_path_cells(
                    a['source'], a['original_dest'], b['source'], b['original_dest']
                ):
                    if cell == a['source'] or cell == b['source']:
                        continue
                    t_a = time_to_reach_cell(
                        a['start_time'], a['original_duration'],
                        a['source'], a['original_dest'], cell,
                    )
                    t_b = time_to_reach_cell(
                        b['start_time'], b['original_duration'],
                        b['source'], b['original_dest'], cell,
                    )
                    if t_a is None or t_b is None:
                        continue
                    if is_earlier_arrival(t_a, a['order'], t_b, b['order']):
                        earlier, later = a, b
                        t_later = t_b
                    else:
                        earlier, later = b, a
                        t_later = t_a
                    leave = time_to_leave_cell(
                        earlier['start_time'], earlier['original_duration'],
                        earlier['source'], earlier['original_dest'], cell,
                    )
                    # None = earlier stays on that square forever (e.g. king arrived).
                    if leave is not None and t_later > leave:
                        continue
                    stop = last_square_before(later['source'], later['original_dest'], cell)
                    better = earlier_stop_along_path(
                        later['source'], later['original_dest'], later['dest'], stop
                    )
                    if better != later['dest']:
                        self._truncate_move(later, better)

        self._resolve_static_path_blocks()

    def _resolve_static_path_blocks(self):
        """Stop movers that would pass through a piece already sitting on the path."""
        moving_ids = set(self.active_moves.keys())
        for move in list(self.active_moves.values()):
            source = move['source']
            original = move['original_dest']
            for cell in path_cells(source, original)[1:]:
                occupant = self.board.piece_at(cell)
                if occupant is None or occupant.id in moving_ids:
                    continue
                if occupant.color == move['piece'].color:
                    stop = last_square_before(source, original, cell)
                else:
                    if cell == original:
                        continue
                    stop = last_square_before(source, original, cell)
                better = earlier_stop_along_path(source, original, move['dest'], stop)
                if better != move['dest']:
                    self._truncate_move(move, better)

    def click(self, x: int, y: int):
        if self.game_over:
            return

        cell = Position(y // self.cell_size, x // self.cell_size)
        if not self.board.is_inside(cell):
            self.selected_cell = None
            self.legal_destinations = set()
            return

        if self.selected_cell is not None:
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
        start_time = self._time_ms

        if not machine.start_move(source, destination, self.cell_size, on_arrived=None):
            return

        self.active_moves[piece.id] = {
            'piece': piece,
            'source': source,
            'dest': destination,
            'original_dest': destination,
            'order': order,
            'start_time': start_time,
            'original_duration': machine.duration_ms,
        }

        def on_arrived(dest: Position):
            move = self.active_moves.pop(piece.id, None)
            if move is None or piece.id not in self.machines:
                return source

            # Effective destination may have been truncated by same-color near-meet.
            dest = move['dest']

            # Opposite-color head-on: later arriver eats the earlier one.
            for other_id, other in list(self.active_moves.items()):
                if other['piece'].color == piece.color:
                    continue
                if other['source'] != dest or other['dest'] != source:
                    continue
                my_arrival = move['start_time'] + machine.duration_ms
                other_machine = self.machines.get(other_id)
                other_arrival = other['start_time'] + (
                    other_machine.duration_ms if other_machine else other['original_duration']
                )
                if is_earlier_arrival(my_arrival, order, other_arrival, other['order']):
                    # We arrived earlier — opponent will eat us when they land.
                    return source
                # We arrived later — eat them on their square.
                self._eliminate(other['piece'], other['source'])

            target = self.board.piece_at(dest)

            if target is not None and target.color == piece.color:
                stop = last_square_before(source, move['original_dest'], dest)
                return self._settle_before_collision(
                    piece, source, stop, abort_animation=False
                )

            if target is not None and target.color != piece.color:
                target_machine = self.machines.get(target.id)
                if target_machine is not None and target_machine.is_jumping:
                    self._eliminate(piece, source)
                    return source
                # Later arriver eats whoever is already on the square.
                self._eliminate(target, dest)

            if piece.id not in self.machines:
                return source

            new_kind = self.promotion.resolve(self.board, piece, dest)
            self.board.move_piece(source, dest, new_kind)
            piece.state = STATE_IDLE
            if new_kind is not None:
                machine.assets = self.loader.load(piece.color, piece.kind)
            return dest if dest != move['original_dest'] else None

        machine._on_arrived = on_arrived
        piece.state = 'moving'
        self._resolve_same_color_path_blocks()

    def tick(self, dt_ms: int):
        if self.game_over:
            return
        self._time_ms += dt_ms
        self._resolve_same_color_path_blocks()
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
