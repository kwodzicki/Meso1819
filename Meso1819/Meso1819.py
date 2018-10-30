#!/usr/bin/env python2.7
import os, shutil, ConfigParser;
import numpy as np;

from PySide import QtCore;
from PySide import QtGui;

from Frames.dateFrame import dateFrame;    

from sharppy.viz.SPCWindow import SPCWindow
from sharppy.io.decoder import getDecoders

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

#############################################
class Meso1819( QtGui.QMainWindow ):
  def __init__(self, parent = None):
    QtGui.QMainWindow.__init__(self);                                           # Initialize the base class
    self.setWindowTitle('Meso 18/19 Sounding Processor');                       # Set the window title
    self.src_dir    = None;                                                     # Set attribute for source data directory to None
    self.dest_dir   = None;                                                     # Set attribute for destination data directory to None
    self.iop_name   = None;                                                     # Set attribute for the IOP name to None
    self.dateFrame  = None;                                                     # Set attribute for the date QFrame to None
    self.skew       = None;                                                     # Set attribute for the skewt plot to None
    self.config     = ConfigParser.RawConfigParser();                           # Initialize a ConfigParser; required for the SPCWidget
    if not self.config.has_section('paths'):                                    # If there is no 'paths' section in the parser
      self.config.add_section( 'paths' );                                       # Add a 'paths' section to the parser

    self.initUI();                                                              # Run method to initialize user interface

  ##############################################################################
  def initUI(self):
    '''
    Method to setup the buttons/entries of the Gui
    '''
    self.dateFrame    = dateFrame( );                                           # Initialize the dateFrame
    self.iop_name     = QtGui.QLineEdit('IOP Name');                            # Initialize Entry widget for the IOP name
    self.sourceButton = QtGui.QPushButton('Source Directory');                  # Initialize button for selecting the source directory
    self.destButton   = QtGui.QPushButton('Destination Directory');             # Initialize button for selecting the destination directory
    self.sourcePath   = QtGui.QLineEdit('');                                    # Initialize entry widget that will display the source directory path
    self.destPath     = QtGui.QLineEdit('');                                    # Initialize entry widget that will display the destination directory path
    self.sourceSet    = indicator();                                            # Initialize an indictor that will appear when the source path is set
    self.destSet      = indicator();                                            # Initialize an indictor that will appear when the destination path is set
    
    self.sourcePath.setEnabled( False );                                        # Disable the sourcePath widget; that way no one can manually edit it
    self.destPath.setEnabled(   False );                                        # Disable the destPath widget; that way no one can manually edit it

    self.sourcePath.hide();                                                     # Hide the source directory path
    self.destPath.hide();                                                       # Hide the destination directory path
    self.sourceSet.hide();                                                      # Hide the source directory indicator
    self.destSet.hide();                                                        # Hide the destination directory indicator

    self.sourceButton.clicked.connect( self.select_source );                    # Set method to run when the source button is clicked 
    self.destButton.clicked.connect(   self.select_dest   );                    # Set method to run when the destination button is clicked

    self.copyButton = QtGui.QPushButton( 'Copy Files' );                        # Create 'Copy Files' button
    self.copyButton.clicked.connect( self.copy_files );                         # Set method to run when 'Copy Files' button is clicked
    self.copyButton.setEnabled(False);                                          # Set enabled state to False; cannot click until after the source and destination directories set

    self.procButton = QtGui.QPushButton( 'Process Files' );                     # Create 'Process Files' button
    self.procButton.clicked.connect( self.proc_files );                         # Set method to run when 'Process Files' button is clicked
    self.procButton.setEnabled(False);                                          # Set enabled state to False; cannot click until after 'Copy Files' completes

    self.genButton = QtGui.QPushButton( 'Generate Sounding' );                  # Create 'Generate Sounding' button
    self.genButton.clicked.connect( self.gen_sounding );                        # Set method to run when 'Generate Sounding' button is clicked
    self.genButton.setEnabled(False);                                           # Set enabled state to False; cannot click until after 'Process Files' completes

    self.uploadButton = QtGui.QPushButton( 'FTP Upload' );                      # Create 'FTP Upload' button
    self.uploadButton.clicked.connect( self.ftp_upload );                       # Set method to run when 'FTP Upload' button is clicked
    self.uploadButton.setEnabled(False);                                        # Set enabled state to False; cannot click until after 'Generate Sounding' completes
    

    grid = QtGui.QGridLayout();                                                 # Initialize grid layout
    grid.setSpacing(10);                                                        # Set spacing to 10
    grid.setColumnStretch(0, 10);                                               # Set column stretch for first column
    grid.setColumnStretch(1,  1);                                               # Set column stretch for second column
    grid.addWidget( self.sourceButton, 0, 0, 1, 1 );                            # Place a widget in the grid
    grid.addWidget( self.sourceSet,    0, 1, 1, 1 );                            # Place a widget in the grid
    grid.addWidget( self.sourcePath,   1, 0, 1, 2 );                            # Place a widget in the grid
    grid.addWidget( self.destButton,   2, 0, 1, 1 );                            # Place a widget in the grid
    grid.addWidget( self.destSet,      2, 1, 1, 1 );                            # Place a widget in the grid
    grid.addWidget( self.destPath,     3, 0, 1, 2 );                            # Place a widget in the grid
    grid.addWidget( self.iop_name,     4, 0, 1, 2 );                            # Place a widget in the grid
    grid.addWidget( self.dateFrame,    5, 0, 1, 2 );                            # Place a widget in the grid
    grid.addWidget( self.copyButton,   6, 0, 1, 2 );                            # Place a widget in the grid
    grid.addWidget( self.procButton,   7, 0, 1, 2 );                            # Place a widget in the grid
    grid.addWidget( self.genButton,    8, 0, 1, 2 );                            # Place a widget in the grid

    centralWidget = QtGui.QWidget();                                            # Create a main widget
    centralWidget.setLayout( grid );                                            # Set the main widget's layout to the grid
    self.setCentralWidget(centralWidget);                                       # Set the central widget of the base class to the main widget
    
    self.show( );                                                               # Show the main widget


  ##############################################################################
  def select_source(self, *args):
    '''
    Method for selecting the source directory of the
    sounding data that was collected
    '''
    self.src_dir = None;                                                        # Set src_dir attribute to None by default
    src_dir = QtGui.QFileDialog.getExistingDirectory();                         # Open a selection dialog
    if src_dir == '': src_dir = None;                                           # If the src_dir is empty string, set src_dir to None
    try:                                                                        # Try to...
      self.src_dir = os.path.realpath( src_dir );                               # Get the real path of the src_dir; updating the src_dir attribute
    except:                                                                     # On exception
      print( 'Error getting real path to source directory' );                   # Print a message

    if self.src_dir is None:                                                    # If the src_dir attribute is None
      self.sourcePath.hide();                                                   # Hide the sourcePath label
      self.sourceSet.hide( );                                                   # Hide the sourceSet icon
      self.copyButton.setEnabled( False );                                      # Make sure that the 'Copy Files' button is disabled
    else:                                                                       # Else
      self.sourcePath.setText( src_dir );                                       # Set the sourcePath label text
      self.sourcePath.show();                                                   # Show the sourcePath label
      self.sourceSet.show( );                                                   # Show the sourceSet icon
      if self.dest_dir is not None:                                             # If the dest_dir attribute is not None
        self.copyButton.setEnabled( True );                                     # Set the 'Copy Files' button to enabled
  ##############################################################################
  def select_dest(self, *args):
    '''
    Method for selecting the destination directory of the
    sounding data that was collected
    '''
    self.dest_dir = None;                                                       # Set dest_dir attribute to None by default
    dest_dir = QtGui.QFileDialog.getExistingDirectory();                        # Open a selection dialog
    if dest_dir == '': dest_dir = None;                                         # If the dest_dir is empty string, set dest_dir to None
    try:                                                                        # Try to...
      self.dest_dir = os.path.realpath( dest_dir );                             # Get the real path of the dest_dir; updating the dest_dir attribute
    except:                                                                     # On exception
      self.dest_dir = None;                                                     # Print a message
                                                                                
    if self.dest_dir is None:                                                   # If the dest_dir attribute is None
      self.destSet.hide( );                                                     # Hide the destPath label
      self.destPath.hide();                                                     # Hide the destSet icon
      self.copyButton.setEnabled( False );                                      # Make sure that the 'Copy Files' button is disabled
    else:                                                                       # Else
      self.destSet.show( );                                                     # Set the destPath label text
      self.destPath.setText( dest_dir )                                         # Show the destPath label
      self.destPath.show()                                                      # Show the destSet icon
      if self.src_dir is not None:                                              # If the src_dir attribute is not None
        self.copyButton.setEnabled( True );                                     # Set the 'Copy Files' button to enabled
  ##############################################################################
  def copy_files(self, *args):
    self.procButton.setEnabled( True );
    return
    if self.dest_dir is None: return;
    if self.src_dir  is None: return;
    if self.iop_name.text() == '': return;                                      # If there is no IOP name specified, then return
    
    dest_dir = os.path.join( self.dest_dir.text, self.iopFrame.iop_name.text() );# Build destination directory using the dest_dir and iop_name
    if not os.path.isdir( dest_dir ): os.make_dirs( dest_dir );                 # IF the dest_dir does NOT exist, then create it
    dest_dir = os.path.join( dest_dir, self.iopFrame.sound_name.text() );       # Append the sound_name to the dest_dir


#     shutil.copy2( src_dir, dest_dir );                                          # Copy all data from the source directory to the dest_dir

  ##############################################################################
  def proc_files(self, *args):
    '''
    Method for processing sounding files;
      i.e., renaming and removing values where ballon is descending in
      sounding
    '''
    print( 'processing' )    
    self.genButton.setEnabled( True );

  ##############################################################################
  def loadArchive(self, filename):
    """
    Get the archive sounding based on the user's selections.
    Also reads it using the Decoders and gets both the stationID and the profile objects
    for that archive sounding.
    """
    for decname, deccls in getDecoders().iteritems():
      try:
        dec = deccls(filename)
        break
      except:
        dec = None
        continue
    
    if dec is None:
      raise IOError("Could not figure out the format of '%s'!" % filename)
    
    profs  = dec.getProfiles()
    stn_id = dec.getStnId()    
    return profs, stn_id
  ##############################################################################
  def gen_sounding(self, *args):
    '''
    Method for generating the SPC-like sounding using the
    SPCWindow class of SHARPpy.
    '''
    print( 'generating' )    
    self.uploadButton.setEnabled( True );
    filename = '/Users/kyle/14061619.sharppy';
    filename = '/Volumes/ExtraHDD/Data/Soundings/LAUNCH154/LAUNCH154_SHARPPY.txt'
    failure = False    
    prof_collection, stn_id = self.loadArchive(filename)
    model = "Archive"
    disp_name = stn_id
    run = prof_collection.getCurrentDate()
    if not failure:
      prof_collection.setMeta('model', model)
      prof_collection.setMeta('run', run)
      prof_collection.setMeta('loc', disp_name)
      
      if not prof_collection.getMeta('observed'):
        # If it's not an observed profile, then generate profile objects in background.
        prof_collection.setAsync(Picker.async)
      
      if self.skew is None:
        self.skew = SPCWindow(cfg=self.config);
        self.skew.closed.connect(self.skewAppClosed);
        self.skew.show();
        self.skew.addProfileCollection(prof_collection)
    else:
      raise exc
    file_name = '/Users/kyle/test_sound.png'
    pixmap = QtGui.QPixmap.grabWidget( self.skew )
    pixmap.save(file_name, 'PNG', 100)
    self.config.set('paths', 'save_img', os.path.dirname(file_name))

  ##############################################################################
  def skewAppClosed(self):
    self.skew = None;
   
  ##############################################################################
  def ftp_upload(self, *args):
    print( 'uploading data' )    


################################################################################
if __name__ == "__main__":
  import sys;
  qt_app = QtGui.QApplication( sys.argv )
  inst = Meso1819( );

  qt_app.exec_();