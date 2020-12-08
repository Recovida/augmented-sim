#!/usr/bin/env python3

import pathlib
import platform
import subprocess
import os
import sys

MODULE = 'augmented_sim.augmented_sim_gui'

here = pathlib.Path(__file__).parent.resolve()
windows = platform.system() == 'Windows'

# Add module directory to path
sys.path.insert(1, str(here))

# If possible, avoid showing a CMD window on Windows
python_executable = sys.executable
pyw = python_executable[:-4] + 'w.exe'
if windows and os.path.isfile(pyw):
    python_executable = pyw

# Run GUI
process = subprocess.Popen(
    [python_executable, '-m', MODULE, *sys.argv[1:]],
    shell=False
)
process.wait()
exit(process.returncode)
