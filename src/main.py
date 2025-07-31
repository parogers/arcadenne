#!/usr/bin/env python3

import xdg
import sys
import pygame

from retroarch import Retroarch


def main():
    rom_path = sys.argv[1]
    retroarch = Retroarch()

    roms = retroarch.find_supported_roms(rom_path)
    print(roms)

    # retroarch.render_game_title(
    #     rom_path=rom_path,
    #     dest_path='out.png',
    # )
    return

    pygame.init()
    display = pygame.display.set_mode((800, 600))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        pygame.display.flip()


if __name__ == '__main__':
    main()
