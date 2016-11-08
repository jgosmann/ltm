# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="ltm",
    version='0.1-dev',
    author="Jan Gosmann",
    author_email="jan@hyper-world.de",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ltm = ltm.main:main'
        ],
    },
)
