import os
import sys

import pygame

import constants
from view.demo_controller import DemoController


HELP_H = 108


def main():
    pygame.init()
    pieces_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'pieces')
    controller = DemoController(pieces_root, constants.CELL_SIZE)
    screen = pygame.display.set_mode(controller.window_size(HELP_H))
    pygame.display.set_caption('KungFuChess Demo')

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
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    if controller.shrink_board():
                        screen = pygame.display.set_mode(controller.window_size(HELP_H))
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    if controller.grow_board():
                        screen = pygame.display.set_mode(controller.window_size(HELP_H))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                controller.click(*event.pos)

        controller.tick(dt_ms)
        screen.fill((30, 30, 30))
        controller.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
