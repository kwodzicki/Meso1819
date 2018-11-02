#!/usr/bin/env python
from setuptools import setup
import setuptools


setuptools.setup(
  name             = "Meso1819",
  description      = "A GUI for moving/renaming sounding files for part of the Meso 18-19 field campaign",
  url              = "https://github.com/kwodzicki/Meso1819",
  author           = "Kyle R. Wodzicki",
  author_email     = "krwodzicki@gmail.com",
  version          = "0.1.9",
  packages         = setuptools.find_packages(),
  install_requires = [ "PySide", "numpy" ],
  scripts          = None,
  zip_safe = False
);
