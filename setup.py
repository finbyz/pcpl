# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in pcpl/__init__.py
from pcpl import __version__ as version

setup(
	name='pcpl',
	version=version,
	description='Prince',
	author='STPL',
	author_email='umesh.garala@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
