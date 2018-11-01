import logging
from PySide import QtGui, QtCore;
from datetime import datetime;
from Meso1819 import settings;

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

################################################################################
class indicator( QtGui.QWidget ): 
  '''
  A QtGui.QWidget subclass to draw green indicators to signify that
  a step as been completed
  '''
  def __init__(self, parent = None):
    QtGui.QWidget.__init__(self, parent)

  def paintEvent(self, event):
    '''
    Method to run on paint events
    '''
    painter = QtGui.QPainter();                                                 # Get a QtGui.QPainter object
    painter.begin(self);                                                        # Begin painting
    painter.setRenderHint( QtGui.QPainter.Antialiasing );                       # Set a rendering option
    painter.setBrush( QtCore.Qt.transparent );                                  # Set the paint brush to transparent
    painter.drawRect( 0, 0, 20, 20 );                                           # Draw a rectangle with width = height = 20
    painter.setBrush( QtCore.Qt.green );                                        # Set the paint brush color to green
    painter.drawEllipse( QtCore.QPoint(10, 10), 9, 9 );                         # Draw a circle that fills most of the rectangle
    painter.end();                                                              # End the painting

################################################################################
class dateFrame( QtGui.QFrame ):
  def __init__(self, parent = None):
    QtGui.QFrame.__init__(self, parent);
    date       = datetime.utcnow()

    self.year       = QtGui.QLineEdit( )
    self.month      = QtGui.QLineEdit( )
    self.day        = QtGui.QLineEdit( )
    self.hour       = QtGui.QLineEdit( )
    
    self.year.setText(  str( date.year  ) );
    self.month.setText( str( date.month ) );
    self.day.setText(   str( date.day   ) );
    self.hour.setText(  str( date.hour  ) );

    year  = QtGui.QLabel('Year')
    month = QtGui.QLabel('Month')
    day   = QtGui.QLabel('Day')
    hour  = QtGui.QLabel('Hour')
    
    grid = QtGui.QGridLayout();
    grid.addWidget( year,   0, 0 );
    grid.addWidget( month,  0, 1 );
    grid.addWidget( day,    0, 2 );
    grid.addWidget( hour,   0, 3 );


    grid.addWidget( self.year,   1, 0 );
    grid.addWidget( self.month,  1, 1 );
    grid.addWidget( self.day,    1, 2 );
    grid.addWidget( self.hour,   1, 3 );
    self.setLayout(grid)
  ############################
  def getDate(self, string = False):
    
    date = datetime( int( self.year.text()  ),
                     int( self.month.text() ),
                     int( self.day.text()   ),
                     int( self.hour.text()  ) );
    if string:
      return date.strftime( settings.date_fmt );
    else:
      return date;
 
