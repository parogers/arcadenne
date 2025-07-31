#!/usr/bin/env python3

import os
import xdg
import sys
import pygame

from retroarch import Retroarch


CONFIG_NAME = 'arcadenne'
TITLES_DIR = xdg.BaseDirectory.save_config_path(CONFIG_NAME, 'titles')


def render_title_cards(retroarch, rom_paths):
    for rom_path in rom_paths:
        dest_path = os.path.join(
            TITLES_DIR,
            os.path.splitext(os.path.basename(rom_path))[0] + '.png'
        )
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
    render_title_cards(retroarch, rom_paths)

    pygame.init()
    display = pygame.display.set_mode((800, 600))
    running = True
    title_map = load_title_cards(resize=display.get_size())
    rom_names = [
        os.path.splitext(os.path.basename(path))[0]
        for path in rom_paths
    ]
    rom_names.sort()

    current_index = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_index = (current_index - 1 + len(rom_names)) % len(rom_names)
                if event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(rom_names)

        img = title_map[rom_names[current_index]]
        display.blit(
            img,
            (
                display.get_width()/2-img.get_width()/2,
                display.get_height()/2-img.get_height()/2
            )
        )
        pygame.display.flip()


if __name__ == '__main__':
    main()
