#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from codecs import open
import jadsh.constants as constants

def readme(fname):
	try:
		import pypandoc
		return pypandoc.convert(fname, "rst")
	except:
		print("warning: pypandoc isn't installed, can't convert from markdown")
		return read(fname)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "jadsh",
	version = constants.VERSION,
	description = "Just Another Dumb SHell",
	long_description = readme("README.md"),
	author = "Bradley Rosenfeld",
	author_email = "thatguy@bradleyrosenfeld.com",
	url = "https://github.com/BoringCode/jadsh/",
	license = "MIT",

	classifiers = [
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: Unix",
		"Topic :: System :: System Shells",
		"Topic :: System :: Shells",
		"Programming Language :: Python :: 2.7"
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5"
	],

	keywords = "jadsh shell terminal unix",

	packages = find_packages(exclude=['jadsh.tests']),

	entry_points = {
		"console_scripts": [
			"jadsh=jadsh:main",
		]
	}
)