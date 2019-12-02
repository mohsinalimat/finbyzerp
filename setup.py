# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in finbyzerp/__init__.py
from finbyzerp import __version__ as version

setup(
	name='finbyzerp',
	version=version,
	description='FinByz ERP',
	author='Finbyz Tech Pvt Ltd',
	author_email='info@finbyz.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
