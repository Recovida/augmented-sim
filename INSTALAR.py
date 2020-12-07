#!/usr/bin/env python3

import pathlib
import platform
import os
import subprocess
import sys

here = pathlib.Path(__file__).parent.resolve()
windows = platform.system() == 'Windows'


def show_msg(*args, **kwargs):
    print(*args, **kwargs)
    if windows:
        print('Pressione Enter para fechar.')
        input()


# Install dependencies
process = subprocess.Popen(
    [sys.executable, '-m', 'pip', 'install', '--user',
     '-r', str(here / 'requirements.txt')])
process.wait()
if process.returncode != 0:
    show_msg('Houve um erro na instalação.')
    exit(1)

# Run setup.py
process = subprocess.Popen([sys.executable, 'setup.py', 'install', '--user'])
process.wait()
if process.returncode == 0:
    os.system('cls' if windows else 'clear')
    show_msg('O programa foi instalado.')
else:
    show_msg('Houve um erro na instalação.')
    exit(1)
