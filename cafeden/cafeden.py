#!/usr/bin/env python3

# Copyright (c) 2021 Coredump Labs
# SPDX-License-Identifier: MIT

import logging
import sys
import threading
import time
from enum import Enum, auto
from pathlib import Path

import keyboard
import mouse
import pystray
from PIL import Image

from .config import AppConfig

CONFIG_FILE_NAME = '.cafeden'
CONFIG_FILES = (Path(__file__).parent / CONFIG_FILE_NAME, Path.home() / CONFIG_FILE_NAME)
ICON_FILE = Path(__file__).parent / 'resources' / 'icon.ico'

# config file schema used for datatype validation and default values
CONFIG_SCHEMA = {
    'general': {
        'idle_threshold': {'type': 'float', 'default': '45.0'},
        'rate': {'type': 'float', 'default': '1.0'},
        'debug': {'type': 'boolean', 'default': 'false'},
    },
    'mouse': {
        'action': {'type': 'mouse_action', 'default': ''},
        'position': {'type': 'coords', 'default': ''},
    },
    'keyboard': {
        'action': {'type': 'keyboard_action', 'default': ''},
        'key': {'type': 'key', 'default': ''},
    }
}

# globals
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config: AppConfig = None

last_interaction = time.time()
is_idle: threading.Event = threading.Event()


class MouseAction(Enum):
    CLICK = auto()
    MOVE = auto()
    PRESS = auto()
    WHEEL = auto()

    @classmethod
    def to_options(cls):
        return ', '.join(k.lower() for k in cls.__members__)


class KeyboardAction(Enum):
    PRESS = auto()
    RELEASE = auto()
    PRESS_AND_RELEASE = auto()

    @classmethod
    def to_options(cls):
        return ', '.join(k.lower().replace('_', ' ') for k in cls.__members__)


def validate_coords(val):
    if val == '':
        return None
    x, y = map(int, val.split(','))
    return x, y


def validate_mouse_action(val):
    action = val.upper().strip()
    if not action:
        action = None
    elif action in MouseAction.__members__:
        action = MouseAction[action]
    else:
        raise Exception(f'valid values are {MouseAction.to_options()}')
    return action


def validate_keyboard_action(val):
    action = val.upper().strip().replace(' ', '_')
    if not action:
        action = None
    elif action in KeyboardAction.__members__:
        action = KeyboardAction[action]
    else:
        raise Exception(f'valid values are {KeyboardAction.to_options()}')
    return action


def validate_key(val):
    if not val:
        return None
    key = keyboard.normalize_name(val)
    key_names = keyboard._canonical_names
    if key not in key_names.canonical_names.values() \
            and key not in key_names.all_modifiers:
        raise Exception(f'"{val}"" is not a valid key')
    return key


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
    global config

    config_validators = {
        'coords': validate_coords,
        'mouse_action': validate_mouse_action,
        'keyboard_action': validate_keyboard_action,
        'key': validate_key,
    }
    config = AppConfig(CONFIG_SCHEMA, config_validators)
    config.read(CONFIG_FILES)

    is_debug = config.getboolean('general', 'debug')
    level = logging.DEBUG if is_debug else logging.INFO
    logging.basicConfig(level=level)
    logger.setLevel(level)

    bg_thread = AutoClicker()

    # TODO: the clicker thread could actually be turned into a function
    # and passed as the setup cb to icon.run()
    icon = create_tray_icon()
    bg_thread.start()
    # blocks here
    icon.run()


def idle_callback(event):
    global last_interaction
    last_interaction = time.time()

    mouse_cfg = config['mouse']
    keyboard_cfg = config['keyboard']

    if is_idle.is_set():
        if mouse_cfg['action'] == 'click' and isinstance(event, mouse.ButtonEvent):
            if event.button == mouse.LEFT:
                # ignore left click events when auto-clicking
                return
        elif mouse_cfg['action'] == 'wheel' and isinstance(event, mouse.WheelEvent):
                # ignore wheel events
                return
        elif keyboard_cfg['action'] and isinstance(event, keyboard.KeyboardEvent):
            if event.name == keyboard_cfg['key']:
                # ignore keyboard events for the key configured
                return
    is_idle.clear()


def setup_hooks(cb):
    keyboard.hook(cb)
    mouse.hook(cb)


class AutoClicker(threading.Thread):
    quanta = .2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True

    def run(self):
        global last_interaction

        setup_hooks(idle_callback)

        idle_threshold = config.getfloat('general', 'idle_threshold')
        action_rate = config.getfloat('general', 'rate')
        mouse_action = config.getmouse_action('mouse', 'action')
        mouse_position = config.getcoords('mouse', 'position')
        keyboard_action = config.getkeyboard_action('keyboard', 'action')
        key_to_press = config.getkey('keyboard', 'key')
        logger.debug(f'mouse action is {mouse_action}')
        logger.debug(f'keyboard action is {keyboard_action}')

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
                    # mouse actions
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
                    # keyboard actions
                    if keyboard_action == KeyboardAction.PRESS:
                        logger.debug('keyboard press')
                        keyboard.press(key_to_press)
                    elif keyboard_action == KeyboardAction.RELEASE:
                        logger.debug('keyboard release')
                        keyboard.release(key_to_press)
                    elif keyboard_action == KeyboardAction.PRESS_AND_RELEASE:
                        logger.debug('keyboard press and release')
                        keyboard.press_and_release(key_to_press)
                time.sleep(self.quanta)

            # restore key state
            if keyboard_action == KeyboardAction.PRESS:
                keyboard.release(key_to_press)
