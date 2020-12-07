#!/usr/bin/env python3

from setuptools import setup, find_packages

import pathlib
import platform


NAME = 'Augmented SIM'
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
    version='0.0.1.dev1',
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


def create_shortcut(directory):
    import os
    import pyshortcuts

    # On Linux, add to some categories
    df = pyshortcuts.linux.DESKTOP_FORM
    add = 'Categories=Office;Spreadsheet;Database;MedicalSoftware;'
    pyshortcuts.linux.DESKTOP_FORM = df.rstrip() + '\n' + add

    cmd = os.path.join(directory, 'augmentedsim_gui')
    kwargs = {
        'name': NAME,
        'description': DESCRIPTION,
        'terminal': False
    }
    pyshortcuts.make_shortcut(cmd, desktop=True, startmenu=True, **kwargs)


def _post_install(setup):
    def _post_install_actions():
        import sys
        if 'install' in sys.argv[1:]:
            create_shortcut(setup.command_obj['install'].install_scripts)
        print('Ok')
    _post_install_actions()
    return setup


setup = _post_install(s)
