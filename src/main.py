#!/usr/bin/env python3

import sys
from dataclasses import dataclass
import ctypes
import tempfile
import os
import logging
import subprocess
import pygame
pygame.init()


logger = logging.getLogger(__name__)


@dataclass
class CoreInfo:
    path: str
    name: str
    version: str
    valid_extensions: list[str]


def run_retroarch(rom_path, core_path, extra_args):
    if not os.path.exists(rom_path):
        raise Exception(f'cannot find rom file: {rom_path}')

    result = subprocess.run([
        '/opt/retroarch/bin/retroarch',
        '-L', core_path,
        rom_path,
        # Without the verbose option, retroarch doesn't log anything even if
        # it runs into an error :/
        '--verbose',
        *extra_args,
    ], capture_output=True)

    if result.returncode != 0:
        separator = '#'*80 + '\n' + '#'*80
        logger.warning(separator)
        logger.warning('Failed to launch retroarch - output follows:\n')
        logger.warning(result.stderr.decode('utf-8'))
        logger.warning(separator)
        raise Exception('failed to launch retroarch')


def render_game_title(rom_path, dest_path, core_path):
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as file:
            file.write('''
audio_driver = "null"
input_driver = "null"
video_driver = "null"
config_save_on_exit = "false"
''')
        run_retroarch(
            rom_path=rom_path,
            core_path=core_path,
            extra_args=[
                '--max-frames=300',
                '--max-frames-ss',
                f'--max-frames-ss-path={dest_path}',
                '--appendconfig', tmp.name,
            ],
        )


def get_core_info(src):
    # Based on struct retro_system_info from libretro-common/include/libretro.h
    class Info(ctypes.Structure):
        _fields_ = [
            ('library_name', ctypes.c_char_p),
            ('library_version', ctypes.c_char_p),
            ('library_valid_extensions', ctypes.c_char_p),
            ('need_fullpath', ctypes.c_bool),
            ('block_extract', ctypes.c_bool),
        ]

    info = Info()
    dll = ctypes.CDLL(src)
    dll.retro_get_system_info(ctypes.pointer(info))

    return CoreInfo(
        path=src,
        name=info.library_name.decode('utf-8'),
        version=info.library_version.decode('utf-8'),
        valid_extensions=info.library_valid_extensions.decode('utf-8').split('|'),
    )


def main():
    rom_path = sys.argv[1]
    info = get_core_info('/home/peter/.config/retroarch/cores/fceumm_libretro.so')
    print('loaded core:', info)

    render_game_title(
        rom_path=rom_path,
        dest_path='out.png',
        core_path=info.path,
    )
    return

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
