# try:
#   import tkinter as tk;
# except:
#   import Tkinter as tk;


from PySide import QtGui;
from datetime import datetime;

class dateFrame( QtGui.QFrame ):
  def __init__(self, parent = None):
    QtGui.QFrame.__init__(self, parent);
    date       = datetime.utcnow()

    self.year       = QtGui.QLineEdit( str( date.year  ) )
    self.month      = QtGui.QLineEdit( str( date.month ) )
    self.day        = QtGui.QLineEdit( str( date.day   ) )
    self.hour       = QtGui.QLineEdit( str( date.hour  ) )

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
    
