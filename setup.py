import os
import sys
from setuptools import setup

version = '0.0.1'

long_description = '''
====
pyriodic
====
is a task scheduler written in Python to run periodic jobs.
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
	py_modules=['pyriodic/pyriodic', 'pyriodic/__init__'],
	author='Anthony Post',
	author_email='postanthony3000 at gmail com',
	maintainer='Anthony Post',
	maintainer_email='postanthony3000 at gmail com',
	url='http://ayehavgunne.github.io/pyriodic/',
	download_url='http://ayehavgunne.github.io/pyriodic/',
	description='A scheduler that uses dateutil to run periodic jobs.',
	long_description=long_description,
	license=bsd_license,
	keywords='schedule periodic job task time timer thread calendar clock queue',
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Programming Language :: Python :: %s.%s' % (sys.version_info[0], sys.version_info[1]),
		'Intended Audience :: Developers'
	]
)