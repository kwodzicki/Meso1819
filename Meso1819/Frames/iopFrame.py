try:
  import tkinter as tk;
except:
  import Tkinter as tk;

class iopFrame( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);

    self.iop_name    = tk.StringVar();
    self.sound_Name  = tk.StringVar();

    self.iop_Label   = tk.Label(self, text = 'IOP Name:');
    self.sound_Label = tk.Label(self, text = 'Sound Name:');

    self.iop_Entry   = tk.Entry(self, textvariable = self.iop_name);     
    self.sound_Entry = tk.Entry(self, textvariable = self.sound_Name); 

    self.iop_Label.grid(   row = 0, column = 0 );
    self.sound_Label.grid( row = 1, column = 0 );

    self.iop_Entry.grid(   row = 0, column = 1 );
    self.sound_Entry.grid( row = 1, column = 1 );
