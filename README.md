# Meso1819

**Meso1819** Python package provides an interacitve GUI to help copy, process,
and upload atmospheric sounding data collected as part of the VORTEX-SE Meso18-19
field campaign. The GUI uses routines and plotting packages from [SHARPpy][SHARPpy]
to generate Skew-T diagrams of soundings.

## Main features

* Compatible with Python2.7
* Platform-independent (Tested on OS X 10.11 and Windows 10)

## Installation

Whenever it's possible, please always use the latest version from the repository.
To install it using `pip`:

    pip install git+https://github.com/kwodzicki/Meso1819

## Dependencies

* [SHARPpy][SHARPpy] - Used to generate SPC-like Skew-T images
* [PySide][PySide]   - Used to generate the GUI; also required by SHARPpy
* [numpy][numpy]     - Used to convert sounding data to SHARPpy format

PySide and numpy should install automatically, however SHARPpy will not and
must be installed manually using pip or whatever package manager you use


## Starting the GUI

To start the GUI, simply run the Meso1819.py command found in the bin/ directory
of this package:

		python /path/to/bin/Meso1819.py

## License

Meso1819 is released under the terms of the GNU GPL v3 license.

[SHARPpy]: https://github.com/sharppy/SHARPpy
[PySide]: https://pypi.org/project/PySide/
[numpy]: https://pypi.org/project/numpy/
