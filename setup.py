import os
import sys
from setuptools import setup
from setuptools import find_packages


version = __import__('pyriodic').__version__


def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


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
	long_description=read('README.md'),
	packages=find_packages(),
	license=read('LICENSE'),
	keywords='schedule scheduler periodic job task time timer thread calendar clock queue',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python :: %s.%s' % (sys.version_info[0], sys.version_info[1]),
		'Intended Audience :: Developers',
		'Topic :: Utilities'
	]
)
