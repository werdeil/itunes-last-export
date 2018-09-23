#!/usr/bin/python
# -*- coding: utf-8 -*-

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="itunes-last-export",
    version="0.0.6",
    author="Vincent Verdeil",
    author_email="vincent.verdeil@gmail.com",
    description="Tool to import playcounts and loved tracks from your last.fm account into iTunes",
    long_description=long_description,
    url="https://github.com/werdeil/itunes-last-export",
    license='GPLv3',
    keywords=[
        'iTunes',
        'Last.fm',
        'scrobble'
    ],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio',
    ),
    packages=setuptools.find_packages(),
    package_data={
        'itunes_last_export.images': ['*.png'],
    },
    include_package_data=True,
    install_requires=[
        'requests'
    ],
    entry_points={'console_scripts': ["itunes-last-export = itunes_last_export.gui:main"]},
)
