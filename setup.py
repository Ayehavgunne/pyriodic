import os
import sys
from setuptools import setup
from setuptools import find_packages

version = '0.0.5'

long_description = '''
====
Pyriodic
====

A job scheduler written in Python to run periodic tasks.
This project was just started and is in the alpha stage so there is a lot yet to do.
Go to http://ayehavgunne.github.io/pyriodic/ for more information.
'''
if os.path.exists('README.rst'):
	with open('README.rst', 'r') as text:
		long_description = text.read()

bsd_license = 'Simplified BSD'

if os.path.exists('LICENSE'):
	with open('LICENSE', 'r') as text:
		bsd_license = text.read()

setup(
    name='pyriodic',
	version=version,
	author='Anthony Post',
	author_email='postanthony3000@gmail.com',
	maintainer='Anthony Post',
	maintainer_email='postanthony3000@gmail.com',
	url='http://ayehavgunne.github.io/pyriodic/',
	download_url='http://ayehavgunne.github.io/pyriodic/',
	description='A job scheduler written in Python to run periodic tasks.',
	long_description=long_description,
	packages=find_packages(),
	license=bsd_license,
	keywords='schedule scheduler periodic job task time timer thread calendar clock queue',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python :: %s.%s' % (sys.version_info[0], sys.version_info[1]),
		'Intended Audience :: Developers',
		'Topic :: Utilities'
	]
)