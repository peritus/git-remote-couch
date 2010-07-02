#!/usr/bin/env python 
from setuptools import setup, find_packages
import platform

long_description = \
  'A git-remote helper that allows you to use a CouchDB as a remote'

name='git_remote_couch'

setup(
    name=name,
    version='0.1',
    url='http://www.python.org/pypi/'+name,
    license='Beerware',
    description='THE BEER-WARE LICENSE',
    author='Filip Noetzel',
    author_email='filip+pypi@j03.de',
    long_description=long_description,
    packages=['git_remote_couch'],
    package_dir={'': 'src',},
    namespace_packages=[],
    include_package_data = True,
    install_requires=[
      'CouchDB==0.7'
    ],
    zip_safe = False,
    extras_require = dict(
        test=[
            'zope.testing',
            'lovely.testlayers==0.1.0a7',
            ]),
    entry_points = {
        'console_scripts' : [
            'git-remote-http+couch = git_remote_couch:main',
            ]
        },
    )
