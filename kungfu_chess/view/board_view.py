import pygame

import constants


LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SELECT = (246, 246, 105)
LEGAL = (100, 200, 100)
LEGAL_CAPTURE = (220, 80, 80)
REST_YELLOW = (255, 220, 40)
REST_OVERLAY = (255, 230, 80, 140)


class BoardView:
    def __init__(self, cell_size: int = constants.CELL_SIZE):
        self.cell_size = cell_size
        self.font = None
        self.small_font = None

    def ensure_fonts(self):
        if self.font is None:
            self.font = pygame.font.SysFont('arial', 18, bold=True)
            self.small_font = pygame.font.SysFont('arial', 14, bold=True)

    def draw(
        self,
        surface,
        board,
        machines,
        selected_cell=None,
        legal_destinations=None,
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

        for piece in board.all_pieces():
            machine = machines.get(piece.id)
            if machine is None:
                continue
            sprite = machine.current_sprite()
            if sprite is None:
                continue
            surface.blit(sprite, (int(machine.pixel_x), int(machine.pixel_y)))

            if machine.is_resting:
                overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                overlay.fill(REST_OVERLAY)
                surface.blit(overlay, (int(machine.pixel_x), int(machine.pixel_y)))
                remaining_s = machine.rest_remaining_ms / 1000.0
                text = self.font.render('{:.1f}s'.format(remaining_s), True, (40, 40, 0))
                text_rect = text.get_rect(
                    center=(
                        int(machine.pixel_x) + self.cell_size // 2,
                        int(machine.pixel_y) + self.cell_size // 2,
                    )
                )
                surface.blit(text, text_rect)

                bar_w = self.cell_size - 16
                bar_h = 8
                bar_x = int(machine.pixel_x) + 8
                bar_y = int(machine.pixel_y) + self.cell_size - 14
                pygame.draw.rect(surface, (80, 80, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                fill_w = int(bar_w * (1.0 - machine.rest_progress))
                pygame.draw.rect(surface, REST_YELLOW, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

        help_lines = [
            'Click piece = select + show legal moves',
            'Click green/red square = move',
            'J = jump selected piece | ESC = quit',
            'Yellow = resting (cooldown)',
        ]
        y = board.height * self.cell_size + 8
        for line in help_lines:
            label = self.small_font.render(line, True, (230, 230, 230))
            surface.blit(label, (8, y))
            y += 18
