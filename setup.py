# Copyright (c) 2021 Coredump Labs
# SPDX-License-Identifier: MIT

import sys
import os
import pathlib
from shutil import rmtree
from setuptools import setup, Command


HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()
BASE_URL = 'https://github.com/coredumplabs/cafeden'
VERSION = '0.1.0'


class AllCommand(Command):

    description = 'Build and publish the package.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        dist = HERE / 'dist'
        if dist.exists():
            print('Cleaning previous builds')
            rmtree(dist)

        print('Building package')
        os.system(f'{sys.executable} setup.py sdist bdist_wheel')

        print('Uploading package')
        os.system(f'{sys.executable} -m twine upload dist/*')


setup(
    name='cafeden',
    version=VERSION,
    description='Simple auto-clicker for keeping your computer awake',
    long_description=README,
    long_description_content_type='text/markdown',
    url=BASE_URL,
    license='MIT License',
    author='Coredump Labs',
    author_email='info@coredumplabs.com',
    download_url=f'{BASE_URL}/releases/tag/v{VERSION}',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    packages=['cafeden'],
    install_requires=['keyboard', 'mouse', 'pystray', 'pillow'],
    entry_points={
        'console_scripts': [
            'cafeden=cafeden.__main__:main',
        ]
    },
    cmdclass={
        'all': AllCommand,
    },
)
