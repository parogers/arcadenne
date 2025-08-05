#!/usr/bin/env python3

import logging
import os
import xdg
import sys
import pygame

from retroarch import Retroarch
from carousel import ImageCarousel


logger = logging.getLogger(__name__)

FPS = 60
CONFIG_NAME = 'arcadenne'
TITLES_DIR = xdg.BaseDirectory.save_config_path(CONFIG_NAME, 'titles')


def render_title_cards(retroarch, rom_paths):
    for rom_path in rom_paths:
        dest_path = os.path.join(
            TITLES_DIR,
            os.path.splitext(os.path.basename(rom_path))[0] + '.png'
        )
        if os.path.exists(dest_path):
            continue
        retroarch.render_game_title(
            rom_path=rom_path,
            dest_path=dest_path,
        )


def load_title_cards(resize=None):
    map = {}
    for fname in os.listdir(TITLES_DIR):
        img = pygame.image.load(os.path.join(TITLES_DIR, fname)).convert()

        scale = min(
            resize[0]/img.get_width(),
            resize[1]/img.get_height()
        )
        if resize:
            new_width = img.get_width()*scale
            new_height = img.get_height()*scale
            img = pygame.transform.scale(img, (new_width, new_height))
        map[os.path.splitext(fname)[0]] = img
    return map


def main():
    rom_path = sys.argv[1]
    retroarch = Retroarch()
    rom_paths = retroarch.find_supported_roms(rom_path)
    if not rom_paths:
        logger.error('No supported roms found. Exiting...')
        sys.exit(1)
    render_title_cards(retroarch, rom_paths)

    pygame.init()
    display = pygame.display.set_mode((800, 600))
    title_map = load_title_cards(resize=display.get_size())
    def get_rom_name(path):
        return os.path.splitext(os.path.basename(path))[0]
    rom_paths.sort(key=lambda path: get_rom_name(path))

    running = True
    carousel = ImageCarousel([
        title_map[get_rom_name(path)]
        for path in rom_paths
    ])
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    carousel.shift_left()
                if event.key == pygame.K_RIGHT:
                    carousel.shift_right()
                if event.key == pygame.K_RETURN:
                    rom_path = rom_paths[carousel.current_index]
                    retroarch.run(rom_path)

        dt = clock.tick(FPS)/1000
        carousel.update(dt)
        carousel.render(display)
        pygame.display.flip()


if __name__ == '__main__':
    main()
