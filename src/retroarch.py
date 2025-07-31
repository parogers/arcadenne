
import xdg
from configparser import ConfigParser
from dataclasses import dataclass
import ctypes
import tempfile
import logging
import os
import subprocess


logger = logging.getLogger(__name__)


CONFIG_NAME = 'retroarch'


@dataclass
class CoreInfo:
    path: str
    name: str
    version: str
    valid_extensions: list[str]


class Retroarch:
    config_dir = xdg.BaseDirectory.save_config_path(CONFIG_NAME)

    def __init__(self):
        self.config = load_cfg(os.path.join(self.config_dir, 'retroarch.cfg'))
        self.cores = load_cores(
            os.path.expanduser(self.config['libretro_directory'])
        )

    def find_cores_for_extension(self, ext):
        '''Returns the list of cores (CoreInfo) that advertise support for the
        given rom extension.'''

        cores = []
        for core in self.cores:
            if ext.lower() in core.valid_extensions:
                cores.append(core)
        return cores

    def run(self, rom_path, extra_args):
        pass

    def render_game_title(self, rom_path, dest_path):
        ext = os.path.splitext(rom_path)[1]
        cores = self.find_cores_for_extension(ext)
        assert cores
        render_game_title(rom_path, dest_path, cores[0].path)

    def find_supported_roms(self, dir):
        '''Returns a list of rom (paths) that are supported by this install of
        retroarch, based on what core plugins are available.'''

        valid_extensions = set().union(
            *(
                core.valid_extensions
                for core in self.cores
            )
        )
        files = []
        for fname in os.listdir(dir):
            ext = os.path.splitext(fname)[1].lower()
            if ext in valid_extensions:
                files.append(os.path.join(dir, fname))
        return files


def load_cfg(path):
    parser = ConfigParser()
    with open(path) as file:
        # Note: workaround for missin allow_unnamed_section in my python version
        parser.read_string('[main]\n' + file.read())

    def _fix_value(value):
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    return {
        key: _fix_value(value)
        for key, value in parser['main'].items()
    }


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


def load_cores(cores_dir):
    cores = []
    for fname in os.listdir(cores_dir):
        if fname.lower().endswith('.so') or fname.lower().endswith('.dll'):
            cores.append(load_core_info(os.path.join(cores_dir, fname)))
    return cores


def load_core_info(src):
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
        # Normalize to how the os module works with extensions
        valid_extensions=[
            '.' + ext
            for ext in info.library_valid_extensions.decode('utf-8').split('|')
        ]
    )
