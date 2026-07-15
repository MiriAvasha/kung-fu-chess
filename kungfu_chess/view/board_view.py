import pygame

import constants


LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SELECT = (246, 246, 105)
LEGAL = (100, 200, 100)
LEGAL_CAPTURE = (220, 80, 80)
REST_YELLOW = (255, 255, 120, 220)
JUMP_GLOW = (120, 220, 255, 160)
JUMP_RING = (80, 200, 255)
TEAM_WHITE = (255, 245, 210)
TEAM_BLACK = (70, 110, 170)
TEAM_RING_WHITE = (255, 230, 150)
TEAM_RING_BLACK = (40, 70, 130)


class BoardView:
    def __init__(self, cell_size: int = constants.CELL_SIZE):
        self.cell_size = cell_size
        self.font = None
        self.small_font = None
        self.big_font = None
        self._tint_cache = {}

    def ensure_fonts(self):
        if self.font is None:
            self.font = pygame.font.SysFont('arial', 18, bold=True)
            self.small_font = pygame.font.SysFont('arial', 14, bold=True)
            self.big_font = pygame.font.SysFont('arial', 54, bold=True)

    def _tinted_sprite(self, sprite, color):
        key = (id(sprite), color)
        cached = self._tint_cache.get(key)
        if cached is not None:
            return cached
        tinted = sprite.copy()
        color_layer = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        color_layer.fill(color + (255,))
        tinted.blit(color_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self._tint_cache[key] = tinted
        return tinted

    def _draw_rest_drain(self, surface, cell, rest_progress: float):
        """Yellow fills the cell; remaining yellow sits at the bottom and shrinks downward."""
        remaining = max(0.0, 1.0 - rest_progress)
        if remaining <= 0.0:
            return
        height = int(round(self.cell_size * remaining))
        if height <= 0:
            return
        cell_x = cell.col * self.cell_size
        cell_y = cell.row * self.cell_size
        yellow = pygame.Surface((self.cell_size, height), pygame.SRCALPHA)
        yellow.fill(REST_YELLOW)
        # Align to bottom of the logical square so yellow drains top -> bottom.
        surface.blit(yellow, (cell_x, cell_y + self.cell_size - height))

    def draw(
        self,
        surface,
        board,
        machines,
        selected_cell=None,
        legal_destinations=None,
        game_over=False,
    ):
        self.ensure_fonts()
        legal_destinations = legal_destinations or set()

        for row in range(board.height):
            for col in range(board.width):
                color = LIGHT if (row + col) % 2 == 0 else DARK
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(surface, color, rect)

                if selected_cell is not None and selected_cell.row == row and selected_cell.col == col:
                    pygame.draw.rect(surface, SELECT, rect, 4)

        for dest in legal_destinations:
            rect = pygame.Rect(
                dest.col * self.cell_size,
                dest.row * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            occupant = board.piece_at(dest)
            marker_color = LEGAL_CAPTURE if occupant is not None else LEGAL
            if occupant is not None:
                pygame.draw.rect(surface, marker_color, rect, 4)
            else:
                center = rect.center
                pygame.draw.circle(surface, marker_color, center, self.cell_size // 8)

        # Rest yellow on logical cells, under the pieces.
        for piece in board.all_pieces():
            machine = machines.get(piece.id)
            if machine is not None and machine.is_resting:
                self._draw_rest_drain(surface, piece.cell, machine.rest_progress)
            if machine is not None and machine.is_jumping:
                glow = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                glow.fill(JUMP_GLOW)
                surface.blit(
                    glow,
                    (piece.cell.col * self.cell_size, piece.cell.row * self.cell_size),
                )

        for piece in board.all_pieces():
            machine = machines.get(piece.id)
            if machine is None:
                continue
            sprite = machine.current_sprite()
            if sprite is None:
                continue

            team_color = TEAM_WHITE if piece.color == 'w' else TEAM_BLACK
            ring_color = JUMP_RING if machine.is_jumping else (
                TEAM_RING_WHITE if piece.color == 'w' else TEAM_RING_BLACK
            )
            draw_x = int(machine.pixel_x)
            draw_y = int(machine.pixel_y)
            center = (draw_x + self.cell_size // 2, draw_y + self.cell_size // 2)
            pygame.draw.circle(surface, ring_color, center, self.cell_size // 2 - 4, 3)

            tinted = self._tinted_sprite(sprite, team_color)
            surface.blit(tinted, (draw_x, draw_y))

            if machine.is_jumping:
                label = self.small_font.render('JUMP', True, (20, 60, 90))
                label_rect = label.get_rect(midtop=(center[0], draw_y + 4))
                surface.blit(label, label_rect)

        if game_over:
            overlay = pygame.Surface((board.width * self.cell_size, board.height * self.cell_size), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))
            label = self.big_font.render('Game Over', True, (255, 230, 80))
            label_rect = label.get_rect(
                center=(board.width * self.cell_size // 2, board.height * self.cell_size // 2)
            )
            surface.blit(label, label_rect)

        help_lines = [
            'Click piece = select + show legal moves',
            'Click same square again = JUMP | green/red = move | ESC = quit',
            'Bright yellow cell = resting (drains top to bottom)',
            'Cyan jump = airborne; attacker landing there is eaten',
        ]
        y = board.height * self.cell_size + 8
        for line in help_lines:
            label = self.small_font.render(line, True, (230, 230, 230))
            surface.blit(label, (8, y))
            y += 18
