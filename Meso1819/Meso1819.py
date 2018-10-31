#!/usr/bin/env python2.7
import logging

import os, shutil, ConfigParser;
import numpy as np;

from PySide import QtCore;
from PySide import QtGui;

from sharppy.viz.SPCWindow import SPCWindow
from sharppy.io.decoder import getDecoders

from QLogger import QLogger
from Frames.dateFrame import dateFrame;    
import settings;

_home    = os.path.expanduser('~');
_desktop = os.path.join( _home, 'Desktop' );

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
    self.dst_dir    = None;                                                     # Set attribute for destination data directory to None
    self.iop_name   = None;                                                     # Set attribute for the IOP name to None
    self.dateFrame  = None;                                                     # Set attribute for the date QFrame to None
    self.skew       = None;                                                     # Set attribute for the skewt plot to None
    self.uploadFiles= None;
    self.config     = ConfigParser.RawConfigParser();                           # Initialize a ConfigParser; required for the SPCWidget
    if not self.config.has_section('paths'):                                    # If there is no 'paths' section in the parser
      self.config.add_section( 'paths' );                                       # Add a 'paths' section to the parser
    
    self.log = logging.getLogger()
    self.log.setLevel( logging.DEBUG );
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
    
    log_handler = QLogger( )
    self.log.addHandler(log_handler)

    grid = QtGui.QGridLayout();                                                 # Initialize grid layout
    grid.setSpacing(10);                                                        # Set spacing to 10
    grid.setColumnStretch(0, 10);                                               # Set column stretch for first column
    grid.setColumnStretch(1,  1);                                               # Set column stretch for second column
    grid.setColumnStretch(2, 10);                                               # Set column stretch for first column
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

    grid.addWidget( log_handler.frame, 0, 2, 9, 1);
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
    self.log.info('Setting the source directory')
    self.src_dir    = None;                                                     # Set src_dir attribute to None by default
    self.uploadFile = None;
    src_dir = QtGui.QFileDialog.getExistingDirectory( dir = _desktop );                         # Open a selection dialog
    if src_dir == '': src_dir = None;                                           # If the src_dir is empty string, set src_dir to None
    try:                                                                        # Try to...
      self.src_dir = os.path.realpath( src_dir );                               # Get the real path of the src_dir; updating the src_dir attribute
    except:                                                                     # On exception
      self.log.warning( 'Error getting real path to source directory' );        # Print a message

    if self.src_dir is None:                                                    # If the src_dir attribute is None
      self.sourcePath.hide();                                                   # Hide the sourcePath label
      self.sourceSet.hide( );                                                   # Hide the sourceSet icon
      self.copyButton.setEnabled( False );                                      # Make sure that the 'Copy Files' button is disabled
    else:                                                                       # Else
      self.sourcePath.setText( src_dir );                                       # Set the sourcePath label text
      self.sourcePath.show();                                                   # Show the sourcePath label
      self.sourceSet.show( );                                                   # Show the sourceSet icon
      if self.dst_dir is not None:                                              # If the dst_dir attribute is not None
        self.uploadFile = [];
        self.copyButton.setEnabled( True );                                     # Set the 'Copy Files' button to enabled
  ##############################################################################
  def select_dest(self, *args):
    '''
    Method for selecting the destination directory of the
    sounding data that was collected
    '''
    self.log.info('Setting the destination directory')
    self.dst_dir    = None;                                                     # Set dst_dir attribute to None by default
    self.uploadFile = None;
    dst_dir = QtGui.QFileDialog.getExistingDirectory( dir = _desktop);                        # Open a selection dialog
    if dst_dir == '': dst_dir = None;                                           # If the dst_dir is empty string, set dst_dir to None
    try:                                                                        # Try to...
      self.dst_dir = os.path.realpath( dst_dir );                               # Get the real path of the dst_dir; updating the dst_dir attribute
    except:                                                                     # On exception
      self.log.warning( 'Error getting real path to destination directory' );   # Print a message
                                                                                
    if self.dst_dir is None:                                                    # If the dst_dir attribute is None
      self.destSet.hide( );                                                     # Hide the destPath label
      self.destPath.hide();                                                     # Hide the destSet icon
      self.copyButton.setEnabled( False );                                      # Make sure that the 'Copy Files' button is disabled
    else:                                                                       # Else
      self.destSet.show( );                                                     # Set the destPath label text
      self.destPath.setText( dst_dir )                                          # Show the destPath label
      self.destPath.show()                                                      # Show the destSet icon
      if self.src_dir is not None:                                              # If the src_dir attribute is not None
        self.uploadFile = [];
        self.copyButton.setEnabled( True );                                     # Set the 'Copy Files' button to enabled
  ##############################################################################
  def copy_files(self, *args):
    '''
    Method for copying files from source to destination, renaming
    files along the way
    '''
    if self.dst_dir is None: 
      self.log.error( 'Destination directory NOT set!' );
      return;
    if self.src_dir  is None:
      self.log.error( 'Source directory NOT set!' );
      return;
    if self.iop_name.text() == '':
      self.log.error( 'IOP Name NOT set!' );
      return;                                                                   # If there is no IOP name specified, then return
    
    date_str     = self.dateFrame.getDate( string = True );                     # Get date string as entered in the gui
    self.dst_dir = os.path.join( self.dst_dir, self.iop_name.text(), date_str );# Build destination directory using the dst_dir and iop_name
    if not os.path.isdir( self.dst_dir ):                                       # If the output directory does NOT exist
      self.log.info( 'Creating directory: ' + self.dst_dir );                   # Log some information
      os.makedirs( dst_dir );                                                   # IF the dst_dir does NOT exist, then create it

    self.log.info( 'Source directory: {}'.format(self.src_dir) );               # Log some information
    self.log.info( 'Destination directory: {}'.format(self.dst_dir) );          # Log some information
    self.log.info( 'Copying directory' );                                       # Log some information
    for root, dirs, files in os.walk( self.src_dir ):                           # Walk over the source directory
      for file in files:                                                        # Loop over all files
        src = os.path.join( root, file );                                       # Set the source file path
        for key in settings.rename:                                             # Loop over the keys in the settings.rename dictionary
          if key in file:                                                       # If the key is in the source file name
            dst_file = settings.rename[key].format(date_str);                   # Set a destination file name
            dst      = os.path.join( dst_dir, dst_file );                       # Build the destination file path
            self.uploadFile.append( dst );                                      # Append the file to the uploadFile list
          else:                                                                 # Else
            dst = os.path.join( dst_dir, file );                                # Set the destination path
        shutil.copy2( src, dst );                                               # Copy all data from the source directory to the dst_dir
        if not os.path.isfile( dst ):                                           # If the destination file does NOT exist
          self.log.error( 'There was an error copying file: {}'.format(file) ); # Log a warning
          # Maybe produce a dialog here?
    self.log.info( 'Finished copying' );                                        # log some information
    self.procButton.setEnabled( True );                                         # Enable the 'Process Files' button
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