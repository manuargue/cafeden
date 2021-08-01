#!/usr/bin/env python3

# Copyright (c) 2021 Coredump Labs
# SPDX-License-Identifier: MIT

import base64
import configparser
import io
import logging
import sys
import threading
import time
from importlib import util
from pathlib import Path

import keyboard
import mouse
import pystray
from PIL import Image


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CONFIG_FILE = Path.home() / '.cafeden'
ICON_FILE = Path(__file__).parent.parent / 'resources' / 'icon.ico'

# globals
last_interaction = time.time()
is_idle = threading.Event()

# config file schema used for datatype validation and default values
config_schema = {
    'general': {
        'idle_threshold': {'type': 'float', 'default': '45.0'},
        'debug': {'type': 'boolean', 'default': 'false'}
    },
    'click': {
        'rate': {'type': 'float', 'default': '1.0'},
        'position': {'type': 'coords', 'default': ''}
    }
}


def coords(val):
    if val == '':
        return None
    x, y = map(int, val.split(','))
    return x, y


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
    config.read(str(CONFIG_FILE))

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
    if is_idle.is_set() and isinstance(event, mouse.ButtonEvent) \
            and event.button == mouse.LEFT:
        # ignore left click events when auto-clicking
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


class AppConfig(configparser.ConfigParser):
    def __init__(self, schema):
        super().__init__(converters={'coords': coords})
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
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.config = config

    def run(self):
        global last_interaction
        last_interaction = time.time()
        setup_hooks(idle_callback)
        idle_threshold = self.config.getfloat('general', 'idle_threshold')
        click_rate = self.config.getfloat('click', 'rate')

        while True:
            logger.debug('waiting for idle')
            is_idle.clear()
            while time.time() - last_interaction < idle_threshold:
                time.sleep(.5)
            logger.debug('idle')

            # perform any one-time action before setting is_idle event
            click_position = self.config.getcoords('click', 'position')
            if click_position:
                mouse.move(*click_position)

            is_idle.set()
            while is_idle.is_set():
                logger.debug('click')
                mouse.click()
                time.sleep(click_rate)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        sys.exit(ex)
