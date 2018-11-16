#!/usr/bin/env python2.7
import logging;
import sys;
from PySide.QtGui import QApplication;
from Meso1819.Meso1819Gui import Meso1819Gui;

log    = logging.getLogger( 'Meso1819' );
log.setLevel( logging.DEBUG );
qt_app = QApplication( sys.argv )
inst   = Meso1819Gui( );

qt_app.exec_();