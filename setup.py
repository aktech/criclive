#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='criclive',
    version='0.1.0',
    description='Live Cricket Scores in Command Line.',
    author='Amit Kumar',
    license='MIT',
    keywords="Cricket score espn scores cli",
    author_email='dtu.amit@gmail.com',
    url='https://github.com/aktech/criclive',
    packages=find_packages(),
    include_package_data = True,
    install_requires=[
        "beautifulsoup4",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'criclive = criclive.main:main'
        ],
    }
)
