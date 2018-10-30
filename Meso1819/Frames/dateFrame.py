try:
  import tkinter as tk;
except:
  import Tkinter as tk;

from datetime import datetime;

class dateFrame( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);
    self.date       = datetime.utcnow()

    self.year       = tk.IntVar();
    self.month      = tk.IntVar();
    self.day        = tk.IntVar();
    self.hour       = tk.IntVar();
    
    self.year.set(  self.date.year  );
    self.month.set( self.date.month );
    self.day.set(   self.date.day   );
    self.hour.set(  self.date.hour  );

    self.frameLabel = tk.Label(self, text = 'Date / Time');
    
    self.yearLabel  = tk.Label(self, text = 'Year: ' );   
    self.monthLabel = tk.Label(self, text = 'Month: ');   
    self.dayLabel   = tk.Label(self, text = 'Day: '  );   
    self.hourLabel  = tk.Label(self, text = 'Hour: ' );
    
    self.yearEntry  = tk.Entry(self, textvariable = self.year  );
    self.monthEntry = tk.Entry(self, textvariable = self.month );
    self.dayEntry   = tk.Entry(self, textvariable = self.day   );
    self.hourEntry  = tk.Entry(self, textvariable = self.hour  );
    
    self.yearEntry.configure(  justify = 'right', width = 5);
    self.monthEntry.configure( justify = 'right', width = 5);
    self.dayEntry.configure(   justify = 'right', width = 5);
    self.hourEntry.configure(  justify = 'right', width = 5);
    
    self.frameLabel.grid( row = 0, column = 0, columnspan = 8 );

    self.yearLabel.grid(  row = 1, column = 0 );
    self.monthLabel.grid( row = 1, column = 2 );
    self.dayLabel.grid(   row = 1, column = 4 );
    self.hourLabel.grid(  row = 1, column = 6 );

    self.yearEntry.grid(  row = 1, column = 1 );
    self.monthEntry.grid( row = 1, column = 3 );
    self.dayEntry.grid(   row = 1, column = 5 );
    self.hourEntry.grid(  row = 1, column = 7 ); 