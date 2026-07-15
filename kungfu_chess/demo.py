import os
import sys

import pygame

import constants
from view.demo_controller import DemoController


def main():
    pygame.init()
    cell = constants.CELL_SIZE
    board_w = 8
    board_h = 8
    help_h = 90
    screen = pygame.display.set_mode((board_w * cell, board_h * cell + help_h))
    pygame.display.set_caption('KungFuChess Demo')

    pieces_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'pieces')
    controller = DemoController(pieces_root, cell)
    clock = pygame.time.Clock()
    running = True

    while running:
        dt_ms = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_j:
                    controller.jump_selected()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                controller.click(*event.pos)

        controller.tick(dt_ms)
        screen.fill((30, 30, 30))
        controller.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
