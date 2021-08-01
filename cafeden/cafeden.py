#!/usr/bin/env python3

# Copyright (c) 2021 Coredump Labs
# SPDX-License-Identifier: MIT

import logging
import sys
import threading
import time
from enum import Enum, auto
from configparser import ConfigParser
from pathlib import Path

import keyboard
import mouse
import pystray
from PIL import Image

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CONFIG_FILE_NAME = '.cafeden'
CONFIG_FILES = (Path() / CONFIG_FILE_NAME, Path.home() / CONFIG_FILE_NAME)
ICON_FILE = Path(__file__).parent.parent / 'resources' / 'icon.ico'

# globals
last_interaction = time.time()
is_idle = threading.Event()

# config file schema used for datatype validation and default values
config_schema = {
    'general': {
        'idle_threshold': {'type': 'float', 'default': '45.0'},
        'rate': {'type': 'float', 'default': '1.0'},
        'debug': {'type': 'boolean', 'default': 'false'},
    },
    'mouse': {
        'action': {'type': 'mouse_action', 'default': ''},
        'position': {'type': 'coords', 'default': ''},
    }
}


class MouseAction(Enum):
    CLICK = auto()
    MOVE = auto()
    PRESS = auto()
    WHEEL = auto()


def coords(val):
    if val == '':
        return None
    x, y = map(int, val.split(','))
    return x, y


def mouse_action(val):
    val = val.upper()
    if not val:
        action = None
    elif val in MouseAction.__members__:
        action = MouseAction[val]
    else:
        raise Exception(', '.join(k.lower() for k in MouseAction.__members__))
    return action


def create_tray_icon():
    def tray_exit_cb(icon):
        icon.visible = False
        icon.stop()

    icon = pystray.Icon('cafeden')
    icon.menu = pystray.Menu(
        pystray.MenuItem('Exit', lambda: tray_exit_cb(icon)),
    )
    icon.icon = Image.open(ICON_FILE)
    icon.title = 'cafeden'
    return icon


def main():
    config = AppConfig(config_schema)
    config.read(CONFIG_FILES)

    is_debug = config.getboolean('general', 'debug')
    level = logging.DEBUG if is_debug else logging.INFO
    logging.basicConfig(level=level)
    logger.setLevel(level)

    bg_thread = AutoClicker(config)

    # TODO: the clicker thread could actually be turned into a function
    # and passed as the setup cb to icon.run()
    icon = create_tray_icon()
    bg_thread.start()
    # blocks here
    icon.run()


def idle_callback(event):
    global last_interaction
    last_interaction = time.time()
    if is_idle.is_set():
        if isinstance(event, mouse.ButtonEvent) and event.button == mouse.LEFT:
            # ignore left click events when auto-clicking
            return
        elif isinstance(event, mouse.WheelEvent):
            # ignore wheel events
            return
    is_idle.clear()


def setup_hooks(cb):
    keyboard.hook(cb)
    mouse.hook(cb)


class ConfigValidationError(Exception):
    def __init__(self, message, section, key):
        super().__init__(message)
        self.section = section
        self.key = key
        self.message = message

    def __str__(self):
        return (f'Invalid value for "{self.key}" under section '
                f'"{self.section}": {self.message}')


class AppConfig(ConfigParser):
    def __init__(self, schema):
        converters = {
            'coords': coords,
            'mouse_action': mouse_action,
        }
        super().__init__(converters=converters)
        # load default values from schema
        self.schema = schema
        self.read_dict({sec: {k: v['default'] for k, v in subsec.items()}
                       for sec, subsec in schema.items()})

    def read(self, filenames, *args):
        super().read(filenames, *args)
        self._validate()

    def _validate(self):
        for section, keys in config_schema.items():
            for key, options in keys.items():
                try:
                    getattr(self, f'get{options["type"]}')(section, key)
                except Exception as ex:
                    raise ConfigValidationError(str(ex), section, key)


class AutoClicker(threading.Thread):
    quanta = .2

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.config: AppConfig = config

    def run(self):
        global last_interaction

        setup_hooks(idle_callback)

        idle_threshold = self.config.getfloat('general', 'idle_threshold')
        action_rate = self.config.getfloat('general', 'rate')
        mouse_action = self.config.getmouse_action('mouse', 'action')
        mouse_position = self.config.getcoords('mouse', 'position')
        logger.debug(f'mouse action is {mouse_action}')

        last_interaction = time.time()
        while True:
            logger.debug('waiting for idle')
            is_idle.clear()
            while time.time() - last_interaction < idle_threshold:
                time.sleep(.5)
            logger.debug('idle')

            # perform any one-time action before setting is_idle event
            if mouse_action:
                if mouse_position:
                    mouse_old_pos = mouse.get_position()
                    mouse.move(*mouse_position)
                if mouse_action == MouseAction.WHEEL:
                    wheel_delta = 1

            is_idle.set()
            last_action = time.time()
            while is_idle.is_set():
                if time.time() - last_action >= action_rate:
                    last_action = time.time()
                    if mouse_action == MouseAction.CLICK:
                        logger.debug('mouse click')
                        mouse.click()
                    elif mouse_action == MouseAction.MOVE:
                        logger.debug('mouse move')
                        if mouse.get_position() == mouse_old_pos:
                            mouse.move(*mouse_position)
                        else:
                            mouse.move(*mouse_old_pos)
                    elif mouse_action == MouseAction.WHEEL:
                        logger.debug('mouse wheel')
                        wheel_delta *= -1
                        mouse.wheel(wheel_delta)
                time.sleep(self.quanta)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        sys.exit(ex)
