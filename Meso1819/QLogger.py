#!/usr/bin/env python2.7
import logging
from PySide import QtGui;
import settings;

class QLogger(logging.Handler):
  '''Code from:
  https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
  '''
  def __init__(self, parent = None, format = settings.log_fmt, level = logging.INFO):
    logging.Handler.__init__(self);                                             # Initialize a log handler as the super class
    self.setFormatter( logging.Formatter( format ) );                           # Set the formatter for the logger
    self.setLevel( level );                                                     # Set the logging level
    self.frame = QtGui.QFrame(parent);                                          # Initialize a QFrame to place other widgets in
    
    self.label      = QtGui.QLabel('Logs');                                     # Define a label for the frame
    self.log_widget = QtGui.QPlainTextEdit();                                   # Initialize a QPlainTextWidget to write logs to
    self.log_widget.verticalScrollBar().minimum();                              # Set a vertical scroll bar on the log widget
    self.log_widget.horizontalScrollBar().minimum();                            # Set a horizontal scroll bar on the log widget
    self.log_widget.setLineWrapMode( self.log_widget.NoWrap );                  # Set line wrap mode to no wrapping
    self.log_widget.setFont( QtGui.QFont("Courier", 12) );                      # Set the font to a monospaced font
    self.log_widget.setReadOnly(True);                                          # Set log widget to read only
    
    layout = QtGui.QVBoxLayout();                                               # Initialize a layout scheme for the widgets
    layout.addWidget( self.label );                                             # Add the label to the layout scheme
    layout.addWidget( self.log_widget );                                        # Add the text widget to the layout scheme

    self.frame.setLayout( layout );                                             # Set the layout of the fram to the layout scheme defined
  def emit(self, record):
    '''
    Overload the emit method so that it prints to the text widget
    '''
    msg = self.format(record)
    self.log_widget.appendPlainText(msg)  
  def write(self, m):
    '''
    Overload the write method so that it does nothing
    '''
    pass;

if __name__ == "__main__":
  import sys;
  qt_app = QtGui.QApplication( sys.argv )
#   inst = QLogger( );
  inst = QLogger2( );

  qt_app.exec_();