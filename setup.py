#!/usr/bin/env python3

from setuptools import setup, find_packages

import pathlib


here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

gitlab_url = 'https://gitlab.com/projeto-fm/mortalidadesp'

s = setup(
    name='augmented_SIM',

    version='0.0.1.dev1',

    description='Um programa que adiciona colunas a uma tabela de óbitos'
                ' codificados segundo SIM',

    long_description=long_description,

    long_description_content_type='text/markdown',

    url=gitlab_url,

    author='FM-USP',
    author_email='palotufo@usp.br',

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

    # package_dir={'': 'augmented_sim'},

    packages=find_packages(),

    python_requires='>=3.6, <4',

    install_requires=[
        'dbfread>=2.0.7',
        'tqdm>=4.54.0',
        'beautifulsoup4>=4.9.3',
        'PyQt5>=5.15.2',
        'python_dateutil>=2.8.1',
    ],

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
    from pyshortcuts import make_shortcut
    make_shortcut(
        os.path.join(directory, 'augmentedsim_gui'),
        name='Augmented SIM',
        description='Adiciona colunas a uma tabela de dados de mortalidade.',
        terminal=False
    )


def _post_install(setup):
    def _post_install_actions():
        create_shortcut(setup.command_obj['install'].install_scripts)
        print('Ok')
    _post_install_actions()
    return setup


setup = _post_install(s)
