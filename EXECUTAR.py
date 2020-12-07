#!/usr/bin/env python3

import pathlib
import platform
import subprocess
import sys

MODULE = 'augmented_sim.augmented_sim_gui'

here = pathlib.Path(__file__).parent.resolve()
windows = platform.system() == 'Windows'

sys.path.insert(1, str(here))

# Run GUI
process = subprocess.Popen(
    [sys.executable, '-m', MODULE, *sys.argv[1:]],
    shell=False
)
process.wait()
exit(process.returncode)
