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
    self.log_widget = QtGui.QTextEdit();                                        # Initialize a QPlainTextWidget to write logs to
    self.log_widget.verticalScrollBar().minimum();                              # Set a vertical scroll bar on the log widget
    self.log_widget.horizontalScrollBar().minimum();                            # Set a horizontal scroll bar on the log widget
    self.log_widget.setLineWrapMode( self.log_widget.NoWrap );                  # Set line wrap mode to no wrapping
    self.log_widget.setFont( QtGui.QFont("Courier", 12) );                      # Set the font to a monospaced font
    self.log_widget.setReadOnly(True);                                          # Set log widget to read only
    
    layout = QtGui.QVBoxLayout();                                               # Initialize a layout scheme for the widgets
    layout.addWidget( self.label );                                             # Add the label to the layout scheme
    layout.addWidget( self.log_widget );                                        # Add the text widget to the layout scheme

    self.frame.setLayout( layout );                                             # Set the layout of the fram to the layout scheme defined
  ##############################################################################
  def emit(self, record):
    '''
    Overload the emit method so that it prints to the text widget
    '''
    msg = self.format(record);                                                  # Format the message for logging
    if record.levelno >= logging.CRITICAL:                                      # If the log level is critical
      self.log_widget.setTextColor( QtCore.Qt.red );                            # Set text color to red
    elif record.levelno >= logging.ERROR:                                       # Elif level is error
      self.log_widget.setTextColor( QtCore.Qt.darkMagenta );                    # Set text color to darkMagenta
    elif record.levelno >= logging.WARNING:                                     # Elif level is warning
      self.log_widget.setTextColor( QtCore.Qt.darkCyan );                       # Set text color to darkCyan
    else:                                                                       # Else
      self.log_widget.setTextColor( QtCore.Qt.black );                          # Set text color to black
    self.log_widget.append(msg);                                                # Add the log to the text widget
  ##############################################################################
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
    self.log   = logging.getLogger( __name__ );
    self.year  = QtGui.QLineEdit( )
    self.month = QtGui.QLineEdit( )
    self.day   = QtGui.QLineEdit( )
    self.hour  = QtGui.QLineEdit( )
    
    year       = QtGui.QLabel('Year')
    month      = QtGui.QLabel('Month')
    day        = QtGui.QLabel('Day')
    hour       = QtGui.QLabel('Hour')
    
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
  def getDate(self):
    '''Method to return datetime object and formatted date string'''
    try:
      date = datetime( int( self.year.text()  ),
                       int( self.month.text() ),
                       int( self.day.text()   ),
                       int( self.hour.text()  ) );
    except:
      self.log.error( 'Must set the date!' );
      self.errorDialog( "Must set the date!!!" )      
      return None, None;

    # Dialog to remind user to make sure date is entered correctly
    dial = QtGui.QMessageBox();                                                 # Initialize a QMessage dialog
    dial.setText( "Are you sure you entered to date correctly?\n\n" + \
      "It MUST be in UTC time!"
    );                                                                          # Set the message for the dialog
    dial.setIcon(QtGui.QMessageBox.Question);                                   # Set the icon for the dialog
    no = dial.addButton('No', QtGui.QMessageBox.RejectRole);                    # Add no button
    dial.addButton('Yes', QtGui.QMessageBox.YesRole);                           # Add a yes button
    dial.exec_();                                                               # Generate the message window
    if dial.clickedButton() == no:                                              # If the user clicked no
      self.log.warning('Canceled because incorrect date');                      # Log a warning
      return None, None;

    return date, date.strftime( settings.date_fmt );
  ##############################################################################
  def resetDate(self):
    '''Method to reset all date entry boxes'''
    self.log.debug( 'Resetting the date' );
    self.year.setText(  '' )
    self.month.setText( '' )
    self.day.setText(   '' )
    self.hour.setText(  '' )
  ##############################################################################
  def errorDialog( self, message ):
    '''Method to generate an error dialog'''
    QtGui.QMessageBox().critical(self, 
      "Caution!", 
      message
    );
 
