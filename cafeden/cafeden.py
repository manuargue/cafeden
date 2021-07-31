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

logging.basicConfig(level=logging.INFO)

CONFIG_FILENAME = '.cafeden'

APP_ICO = """
iVBORw0KGgoAAAANSUhEUgAAAMgAAACmCAYAAACfpsC0AAAC83pUWHRSYXcgcHJvZmlsZSB0eXBlIGV
4aWYAAHja7ZZdrtwgDIXfWUWXENsYm+UQfqTuoMvvgSTTmblzpVv1vlSaoABj4AD+DJnQf/0c4Qce8p
hCVPOUU9rwxBwzF1R8O56yctriytdTrzZ6tIeSzgaGSVDK8dNPO112ugkcRUFN74S8ng37Y0OOp74/C
Z0TyVwRo9JOoXwKCR8NdAqUY1tbym73W9j7UZ7jDzfgDTMTW9o3keff0eC9pjAKcxeSDTlLPBYg86Ug
BRVFTpJmR6SC3448Cp0rgUNe+Wm7W1V4pnKrPVFp8TUUSUePAMOjM9OtfGknfe38sFx8N7PUs8aP9iG
L6cN2rneM5mGMfuyuxASXpnNT1xZXDR13uFzWsIRkeBV1WykjeUD0VtBpW912pEqZGFgGRWpUaFBfZa
WKJUbubCiZK0BNm4tx5ipbAK04Ew02ydLAi6UCr8DKt7XQmjev6So5Jm6EnkwQo8k6LODfkD4VGmOGP
NF0JtDT4kM8AxXLmORmjl4AQuOKI10OvtLzM7kKCOpys2ODZdsPiV3pjK0ZR7JAT7yK8gg8snYKwEWY
W7EYEhDYEolSos2YjQh+dPApEHIcGt6BgFS5YZUcBafF2HnOjTFGqy8rH2bcWQChksSAJksBq4iLDfF
j0RFDRUWjqiY1dc1akqSYNKVkaV5+xcSiqSUzc8tWXDy6enJzD569ZM6Cy1FzypY951wKJi1QLhhd0K
GUnXfZ46572m33Pe+lInxqrFpTteqh5loaN2m4J1pq1rzlVjp1hFKPXXvq1r3nXgZCbciIQ0caNnzkU
W7UKBxYP6SvU6OLGi9Ss6PdqGGo2SVB8zrRyQzEOBKI2ySAgObJbHOKkcNEN5ltmXEqlLFKnXAaTWIg
GDuxDrqx+0PugVuI8Z+48UUuTHTfQS5MdJ+Q+8jtBbU2vzZ1k7AIzWM4nboJjh86dC/sZX7UvlyGvx3
wFnoLvYXeQm+ht9B/IzTw5cz4h/obRcxk8/pdZDwAAAGEaUNDUElDQyBwcm9maWxlAAB4nH2RPUjDQB
zFX1OLIpUKdhBxyFCdLIhfOEoVi2ChtBVadTC59AuaNCQpLo6Ca8HBj8Wqg4uzrg6ugiD4AeLm5qToI
iX+Lym0iPHguB/v7j3u3gFCo8JUs2scUDXLSMVjYja3Kna/IoB+hDCNqMRMPZFezMBzfN3Dx9e7KM/y
Pvfn6FPyJgN8IvEc0w2LeIN4ZtPSOe8Th1lJUojPiccMuiDxI9dll984Fx0WeGbYyKTmicPEYrGD5Q5
mJUMlniKOKKpG+ULWZYXzFme1UmOte/IXBvPaSprrNIcRxxISSEKEjBrKqMBClFaNFBMp2o95+Iccf5
JcMrnKYORYQBUqJMcP/ge/uzULkxNuUjAGBF5s+2ME6N4FmnXb/j627eYJ4H8GrrS2v9oAZj9Jr7e1y
BEQ2gYurtuavAdc7gCDT7pkSI7kpykUCsD7GX1TDhi4BXrX3N5a+zh9ADLU1fINcHAIjBYpe93j3T2d
vf17ptXfD9tTctFib3vbAAANGGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2l
uPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PS
JhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNC40LjAtRXhpdjIiPgogPHJkZjpSREYge
G1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8
cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9
iZS5jb20veGFwLzEuMC9tbS8iCiAgICB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YX
AvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kY
y9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6R0lNUD0iaHR0cDovL3d3dy5naW1wLm9yZy94bXAvIgog
ICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iCiAgICB4bWxuczp4bXA
9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iCiAgIHhtcE1NOkRvY3VtZW50SUQ9ImdpbXA6ZG
9jaWQ6Z2ltcDplM2Q0ODRkNi0xYzJkLTQ3ZDItODk1NC1mYTEwM2Y5Zjc5ODYiCiAgIHhtcE1NOkluc
3RhbmNlSUQ9InhtcC5paWQ6OGEyYmUyNmMtYzRiZC00Y2UyLTg3NTEtMzZkN2U3N2I0Zjg0IgogICB4
bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6ZDRhYjM0MTktZDVlYi00YWM5LWE4OGUtN2E
yNmRmYjEwOTU0IgogICBkYzpGb3JtYXQ9ImltYWdlL3BuZyIKICAgR0lNUDpBUEk9IjIuMCIKICAgR0
lNUDpQbGF0Zm9ybT0iV2luZG93cyIKICAgR0lNUDpUaW1lU3RhbXA9IjE2MjExODA3MjE1Nzc0NzAiC
iAgIEdJTVA6VmVyc2lvbj0iMi4xMC4yNCIKICAgdGlmZjpPcmllbnRhdGlvbj0iMSIKICAgeG1wOkNy
ZWF0b3JUb29sPSJHSU1QIDIuMTAiPgogICA8eG1wTU06SGlzdG9yeT4KICAgIDxyZGY6U2VxPgogICA
gIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJzYXZlZCIKICAgICAgc3RFdnQ6Y2hhbmdlZD0iLy
IKICAgICAgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDoxN2Y5NWNhNS1iMTEwLTQ1ODktOTIwYy0xZ
WRiOTNmM2Y4YjciCiAgICAgIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkdpbXAgMi4xMCAoV2luZG93cyki
CiAgICAgIHN0RXZ0OndoZW49IjIwMjEtMDUtMTZUMjI6NTg6NDEiLz4KICAgIDwvcmRmOlNlcT4KICA
gPC94bXBNTTpIaXN0b3J5PgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbW
V0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIA
ogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+prj
lEgAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB+UFEA86KX7j+V
YAAAo2SURBVHja7Z1ZrF1VGcd/pcXSAVooLaMIbaUVQ2kKSESTUlFARKMiGpUg8NBgIqEvhjgFE6VqQ
jQoJlpETRSsGAccHyy0UKHxwaFBSwXuLZ0pHZDaiZbb+rA25bLPuvfse8a9z/r9kv1w17nnZK/1ff/9
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"""

# globals
last_interaction = time.time()
is_idle = threading.Event()

# config file schema used for datatype validation and default values
config_schema = {
    'general': {
        'idle_threshold': {'type': 'float', 'default': '45.0'},
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
    icon.icon = Image.open(io.BytesIO(base64.b64decode(APP_ICO)))
    icon.title = 'cafeden'
    return icon


def main():
    config = AppConfig(config_schema)
    config.read(str(Path.home().joinpath(CONFIG_FILENAME)))

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
                '"{self.section}": {self.message}')


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
            logging.debug('waiting for idle')
            is_idle.clear()
            while time.time() - last_interaction < idle_threshold:
                time.sleep(.5)
            logging.debug('idle')

            # perform any one-time action before setting is_idle event
            click_position = self.config.getcoords('click', 'position')
            if click_position:
                mouse.move(*click_position)

            is_idle.set()
            while is_idle.is_set():
                logging.debug('click')
                mouse.click()
                time.sleep(click_rate)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        sys.exit(ex)
