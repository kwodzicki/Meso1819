#!/usr/bin/env python
import setuptools
from distutils.util import convert_path

main_ns  = {};
ver_path = convert_path("Meso1819/version.py");
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns);

setuptools.setup(
  name             = "Meso1819",
  description      = "A GUI for moving/renaming sounding files for part of the Meso 18-19 field campaign",
  url              = "https://github.com/kwodzicki/Meso1819",
  author           = "Kyle R. Wodzicki",
  author_email     = "krwodzicki@gmail.com",
  version          = main_ns['__version__'],
  packages         = setuptools.find_packages(),
  install_requires = [ "PySide", "numpy" ],
  scripts          = ['bin/runMeso1819.py'],
  zip_safe         = False
);
