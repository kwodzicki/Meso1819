#!/usr/bin/env python2.7
import sys;
from PySide import QtGui;
from Meso1819.Meso1819Gui import Meso1819Gui;

qt_app = QtGui.QApplication( sys.argv )
inst   = Meso1819Gui( );

qt_app.exec_();