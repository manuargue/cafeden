<!-- Copyright (c) 2021 Coredump Labs -->
<!-- SPDX-License-Identifier: MIT -->

# cafeden :coffee:

## Overview

`cafeden` (from Vietnamese "cafe đen" or "black coffee") is a simple auto-clicker for keeping your computer awake. It monitors mouse and keyboard events to detect when the user is idle.

## How to run :running::dash:

1. Download and install [Python 3](https://www.python.org/downloads) :snake:

2. Open a terminal (e.g. cmd on Windows) and install the package with [PIP](https://pypi.org/project/pip/)
    ```bash
    pip install cafeden
    ```

3. Next, launch the application by running in the terminal:
    ```bash
    cafeden
    ```
    > Note: make sure the Python Scripts directory is in your PATH (e.g. `C:\Users\myuser\AppData\Local\Programs\Python\Python3x\Scripts`)

4. A system tray icon with a [phin cà phê](https://en.wikipedia.org/wiki/Vietnamese_iced_coffee) will appear. To quit the application, right-click on the icon and click on "Exit".

## Configuration :wrench:

Configuration is optional and is done through an [INI configuration file](https://en.wikipedia.org/wiki/INI_file). To setup the configuration, create a file named `.cafeden` in your home directory (e.g. `~/.cafeden` in Linux and `C:\Users\myuser\.cafeden` in Windows systems). Default values, allowed sections and options are shown below.

```ini
[general]
# Time in seconds since the last mouse/keyboard event from which the user is considered to be idle
idle_threshold = 45.0

[click]
# click rate in seconds
rate = 1.0
# position as in: x, y. Empty means click wherever the mouse is
position =
```

## OS Supported :computer:

- Windows 10 :heavy_check_mark:
- GNU/Linux :question: (not tested)
    - requires one of: Xorg, GNOME and Ubuntu
    - requires running as root
- macOS :question: (not tested)

## License :page_with_curl:

Copyright &copy; 2021 Coredump Labs

Licensed under MIT: https://opensource.org/licenses/MIT
