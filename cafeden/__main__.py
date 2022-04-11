#!/usr/bin/env python3

# Copyright (c) 2021-2022 Manuel Arguelles
# SPDX-License-Identifier: MIT

import sys
from .cafeden import main


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        sys.exit(ex)
