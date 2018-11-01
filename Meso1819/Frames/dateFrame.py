# try:
#   import tkinter as tk;
# except:
#   import Tkinter as tk;


from PySide import QtGui;
from datetime import datetime;
from Meso1819.settings import date_fmt

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
      return date.strftime( date_fmt );
    else:
      return date;
 
