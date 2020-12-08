#!/usr/bin/env python3

from setuptools import setup, find_packages

import os
import pathlib
import platform


NAME = 'Augmented SIM'
VERSION = '0.0.1.dev1'
YEAR = 2020
DESCRIPTION = 'Programa que adiciona colunas a uma tabela de óbitos' \
              ' codificados segundo o SIM'
PACKAGE_NAME = 'augmented_SIM'
GIT_URL = 'https://gitlab.com/projeto-fm-usp-mortalidade-sp/augmented-sim'


here = pathlib.Path(__file__).parent.resolve()
LONG_DESCRIPTION = (here / 'README.md').read_text(encoding='utf-8')
DEPENDENCIES = (here / 'requirements.txt') \
                .read_text(encoding='utf-8').strip().split('\n')

here = pathlib.Path(__file__).parent.resolve()
windows = platform.system() == 'Windows'

s = setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url=GIT_URL,

    # author='FM-USP',
    # author_email='palotufo@usp.br',

    classifiers=[
        #  3 - Alpha; 4 - Beta; 5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='SIM, mortality, healthcare, ICD',

    packages=find_packages(),
    python_requires='>=3.6, <4',
    install_requires=DEPENDENCIES,

    entry_points={
        'console_scripts': [
            'augmentedsim_cli=augmented_sim.augmented_sim_cli:main',
        ],
        'gui_scripts': [
            'augmentedsim_gui=augmented_sim.augmented_sim_gui:main',
        ],
    },

    # project_urls={  # Optional
    #     'Bug Reports': gitlab_url + '/-/issues',
    #     'Source': gitlab_url,
    # },

)


def create_shortcut(file_name):
    import pyshortcuts

    # On Linux, add to some categories
    df = pyshortcuts.linux.DESKTOP_FORM
    add = 'Categories=Office;Spreadsheet;Database;MedicalSoftware;'
    pyshortcuts.linux.DESKTOP_FORM = df.rstrip() + '\n' + add

    cmd = file_name
    kwargs = {
        'name': NAME,
        'description': DESCRIPTION,
        'terminal': False
    }
    pyshortcuts.make_shortcut(cmd, desktop=True, startmenu=True, **kwargs)


def _create_custom_entry_point(file_name):
    # The file generated by setuptools has an invalid encoding
    contents = """import subprocess, sys;""" \
        """process = subprocess.Popen([sys.executable, '-m', """ \
        """'augmented_sim.augmented_sim_gui',*sys.argv[1:]],shell=False);""" \
        """process.wait(); exit(process.returncode)"""
    with open(file_name, 'w', encoding='utf-8') as fd:
        print(contents, file=fd, end='')


def _post_install(setup):
    def _post_install_actions():
        directory = setup.command_obj['install'].install_scripts
        gui_script = os.path.join(directory, 'augmentedsim_gui')
        import sys
        if 'install' in sys.argv[1:]:
            if windows:
                if os.path.isfile(sys.executable[:-4] + 'w.exe'):
                    gui_script += '_custom.py'
                    _create_custom_entry_point(gui_script)
            create_shortcut(gui_script)
        print('Ok')
    _post_install_actions()
    return setup


setup = _post_install(s)
