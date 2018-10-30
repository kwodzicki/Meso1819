#!/usr/bin/env python2.7
import os, shutil;

try:
  import tkinter as tk;
  from tkinter import FileDialog;
except:
  import Tkinter as tk;
  import tkFileDialog as FileDialog;  

from Frames.dateFrame import dateFrame;    
from Frames.iopFrame  import iopFrame;    

#############################################
class Meso1819( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);
    self.dateFrame  = dateFrame( self );
    self.iopFrame   = iopFrame(  self );
    self.source_dir = None;
    self.dest_dir   = None;
    
    self.source_But = tk.Button(self, text = 'Source Directory')
    self.source_But.configure( command = self.select_source );

    self.dest_But = tk.Button(self, text = 'Destination Directory')
    self.dest_But.configure( command = self.select_dest );

    self.run_But = tk.Button(self, text = 'Run');
    self.run_But.configure( command = self.run )
    
    self.source_But.pack( padx = 5, pady = 5, fill = 'both', expand = True );
    self.dest_But.pack(   padx = 5, pady = 5, fill = 'both', expand = True );
    self.iopFrame.pack(   padx = 5, pady = 5 );
    self.dateFrame.pack(  padx = 5, pady = 5 );
    self.run_But.pack(    padx = 5, pady = 5, fill = 'both', expand = True );

    self.pack( )
  ##############################################################################
  def select_source(self, *args):
    '''
    Method for selecting the source directory of the
    sounding data that was collected
    '''
    self.source_dir = FileDialog.askdirectory( 
      title = "Select sounding directory"
    );
    try:
      self.source_dir = os.path.realpath( self.source_dir );
    except:
      return;
  ##############################################################################
  def select_dest(self, *args):
    '''
    Method for selecting the source directory of the
    sounding data that was collected
    '''
    self.dest_dir = FileDialog.askdirectory( 
      title = "Select destination directory"
    );
    try:
      self.dest_dir = os.path.realpath( self.dest_dir );
    except:
      return;
  ##############################################################################
  def run(self, *args):
    dest_dir = self.dest_dir.get();                                             # Get the destination directory
    if dest_dir == '': return;                                                  # If the dest dir is empty the return
    
    iop_name = self.iopFrame.iop_name.get();                                    # Get the iop name 
    if iop_name == '': return;                                                  # If there is no IOP name specified, then return

    sound_name = self.iopFrame.sound_name.get();                                # Get the sounding name
    if sound_name == '': return;                                                # If there is no sounding name specified, then return
    
    dest_dir = os.path.join( dest_dir, iop_name );                              # Build destination directory using the dest_dir and iop_name
    if not os.path.isdir( dest_dir ): os.make_dirs( dest_dir );                 # IF the dest_dir does NOT exist, then create it
    dest_dir = os.path.join( dest_dir, sound_name );                            # Append the sound_name to the dest_dir

#     shutil.copy2( src_dir, dest_dir );                                          # Copy all data from the source directory to the dest_dir
    

################################################################################
if __name__ == "__main__":
  root = tk.Tk();
  inst = Meso1819( root );
  root.mainloop();