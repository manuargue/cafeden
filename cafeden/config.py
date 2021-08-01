#!/usr/bin/env python3

# Copyright (c) 2021 Coredump Labs
# SPDX-License-Identifier: MIT

from configparser import ConfigParser


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
    def __init__(self, schema: dict, validators: dict = None):
        super().__init__(converters=validators)
        # load default values from schema
        self.schema: dict = schema
        self.read_dict({sec: {k: v['default'] for k, v in subsec.items()}
                       for sec, subsec in schema.items()})

    def read(self, filenames, *args):
        super().read(filenames, *args)
        self._validate()

    def _validate(self):
        for section, keys in self.schema.items():
            for key, options in keys.items():
                try:
                    getattr(self, f'get{options["type"]}')(section, key)
                except Exception as ex:
                    raise ConfigValidationError(str(ex), section, key)
