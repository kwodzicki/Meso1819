import logging

import os, shutil, ConfigParser;
import numpy as np;

from PySide import QtCore;
from PySide import QtGui;

from sharppy.viz.SPCWindow import SPCWindow
from sharppy.io.decoder import getDecoders

from iMet2SHARPpy import iMet2SHARPpy;
from widgets import QLogger, dateFrame, indicator;
import settings;

_home    = os.path.expanduser('~');
_desktop = os.path.join( _home, 'Desktop' );

#############################################
class Meso1819Gui( QtGui.QMainWindow ):
  def __init__(self, parent = None):
    QtGui.QMainWindow.__init__(self);                                           # Initialize the base class
    self.setWindowTitle('Meso 18/19 Sounding Processor');                       # Set the window title
    self.src_dir     = None;                                                    # Set attribute for source data directory to None
    self.dst_dir     = None;                                                    # Set attribute for destination data directory to None
    self.dst_dirFull = None;                                                    # Set attribute for destination data directory to None
    self.iopName     = None;                                                    # Set attribute for the IOP name to None
    self.dateFrame   = None;                                                    # Set attribute for the date QFrame to None
    self.date        = None;
    self.date_str    = None;                                                    # Set attribute for date string
    self.skew        = None;                                                    # Set attribute for the skewt plot to None
    self.sndDataFile = None;                                                    # Set attribute for sounding data input file
    self.sndDataPNG  = None;                                                    # Set attribute for sounding image file
    self.uploadFiles = None;                                                    # Set attribute for list of files to upload to ftp
    self.config      = ConfigParser.RawConfigParser();                          # Initialize a ConfigParser; required for the SPCWidget
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
    self.iopLabel     = QtGui.QLabel('IOP Number');                             # Initialize Entry widget for the IOP name
    self.iopName      = QtGui.QLineEdit();                                      # Initialize Entry widget for the IOP name
    self.stationLabel = QtGui.QLabel('Station Name');                           # Initialize Entry widget for the IOP name
    self.stationName  = QtGui.QLineEdit();                                      # Initialize Entry widget for the IOP name
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
#     self.sourceSet.show();                                                      # Hide the source directory indicator
#     self.destSet.show();                                                        # Hide the destination directory indicator

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

    self.checkButton = QtGui.QPushButton( 'Check website' );                    # Create 'Check website' button
    self.checkButton.clicked.connect( self.check_site );                        # Set method to run when 'Check website' button is clicked
    self.checkButton.setEnabled(False);                                         # Set enabled state to False; cannot click until after 'FTP Upload' completes
    
    log_handler = QLogger( );                                                   # Initialize a QLogger logging.Handler object
    self.log.addHandler(log_handler);                                           # Add the Handler object to the logger

    grid = QtGui.QGridLayout();                                                 # Initialize grid layout
    grid.setSpacing(10);                                                        # Set spacing to 10
    for i in range(4): 
      grid.setColumnStretch(i,  0);                                             # Set column stretch for ith column
      grid.setColumnMinimumWidth(i,  60);                                       # Set column min width for ith column
    grid.setColumnStretch(4,  0);                                               # Set column stretch for 5th column
    grid.setColumnMinimumWidth(4,  20);                                         # Set column min width for 5th column
    
    grid.addWidget( self.sourceButton,  0, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.sourceSet,     0, 4, 1, 1 );                           # Place a widget in the grid
    grid.addWidget( self.sourcePath,    1, 0, 1, 5 );                           # Place a widget in the grid

    grid.addWidget( self.destButton,    2, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.destSet,       2, 4, 1, 1 );                           # Place a widget in the grid
    grid.addWidget( self.destPath,      3, 0, 1, 5 );                           # Place a widget in the grid

    grid.addWidget( self.iopLabel,      4, 0, 1, 2 );                           # Place a widget in the grid
    grid.addWidget( self.iopName,       5, 0, 1, 2 );                           # Place a widget in the grid

    grid.addWidget( self.stationLabel,  4, 2, 1, 2 );                           # Place a widget in the grid
    grid.addWidget( self.stationName,   5, 2, 1, 2 );                           # Place a widget in the grid

    grid.addWidget( self.dateFrame,     6, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.copyButton,    7, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.procButton,    8, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.genButton,     9, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.uploadButton, 10, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.checkButton,  11, 0, 1, 4 );                           # Place a widget in the grid

    grid.addWidget( log_handler.frame, 0, 6, 12, 1);
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
#       self.src_dir = os.path.realpath( src_dir );                               # Get the real path of the src_dir; updating the src_dir attribute
      self.src_dir = src_dir;                                                   # Udating the src_dir attribute
    except:                                                                     # On exception
      self.log.warning( 'Error getting real path to source directory' );        # Print a message

    if self.src_dir is None:                                                    # If the src_dir attribute is None
      self.sourcePath.hide();                                                   # Hide the sourcePath label
      self.sourceSet.hide( );                                                   # Hide the sourceSet icon
      self.copyButton.setEnabled( False );                                      # Make sure that the 'Copy Files' button is disabled
    else:                                                                       # Else
      self.sourcePath.setText( src_dir );                                       # Set the sourcePath label text
      self.sourcePath.show();                                                   # Show the sourcePath label
      self.sourceSet.show();                                                    # Show the sourceSet icon
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
#       self.dst_dir = os.path.realpath( dst_dir );                               # Get the real path of the dst_dir; updating the dst_dir attribute
      self.dst_dir = dst_dir;                                                   # Udating the dst_dir attribute
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
    failed = False;                                                             # Initialize failed to False
    if self.dst_dir is None: 
      self.log.error( 'Destination directory NOT set!' );
      return;
    if self.src_dir  is None:
      self.log.error( 'Source directory NOT set!' );
      return;

    if self.iopName.text() == '':
      self.log.error( 'IOP Number NOT set!!!' )
      self.errorDialog( "Must set the IOP Number!!!" );
      return
    if self.stationName.text() == '':
      self.log.error( 'IOP Number NOT set!!!' )
      self.errorDialog( "Must set the Station Name!!!");
      return

    
    self.date, self.date_str = self.dateFrame.getDate( );                       # Get datetime object and date string as entered in the gui
    if self.date_str is None:
      self.log.error( 'Date not set!!!' );
      return;
    self.dst_dirFull  = os.path.join( 
      self.dst_dir, self.iopName.text(), self.date_str 
    );                                                                          # Build destination directory using the dst_dir and iopName
    if not os.path.isdir( self.dst_dirFull ):                                   # If the output directory does NOT exist
      self.log.info( 'Creating directory: ' + self.dst_dirFull );               # Log some information
      os.makedirs( self.dst_dir );                                              # IF the dst_dir does NOT exist, then create it
    else:                                                                       # Else, the directory exists, so check to over write
      dial = QtGui.QMessageBox()
      dial.setText( "The destination directory exists!\n" + \
        "Do you want to overwrite it?\n" + \
        "YOU CANNOT UNDO THIS ACTION!!!" 
      );
      dial.setIcon(QtGui.QMessageBox.Question)
      yes = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
      dial.addButton('No', QtGui.QMessageBox.RejectRole)
      dial.exec_()
      if dial.clickedButton() == yes:
        self.log.info( 'Removing directory: ' + self.dst_dirFull );             # Log some information
        shutil.rmtree( self.dst_dirFull );                                      # Delete the directory
        self.log.info( 'Creating directory: ' + self.dst_dirFull );             # Log some information
        os.makedirs( self.dst_dirFull );                                        # IF the dst_dir does NOT exist, then create it
      else:                                                                     # Else, don't do anything
        self.log.warning('Cannot over write data!');                            # Log a warning
        return;                                                                 # Return from function

    self.log.info( 'Source directory: {}'.format(self.src_dir) );               # Log some information
    self.log.info( 'Destination directory: {}'.format(self.dst_dirFull) );      # Log some information
    self.log.info( 'Copying directory' );                                       # Log some information
    for root, dirs, files in os.walk( self.src_dir ):                           # Walk over the source directory
      for file in files:                                                        # Loop over all files
        src = os.path.join( root, file );                                       # Set the source file path
        dst = os.path.join( self.dst_dirFull, file );                           # Set the destination path
        shutil.copy2( src, dst );                                               # Copy all data from the source directory to the dst_dir
        if not os.path.isfile( dst ):                                           # If the destination file does NOT exist
          self.log.error( 'There was an error copying file: {}'.format(file) ); # Log a warning
          falied = True;                                                        # Set failed to True
          # Maybe produce a dialog here?
    if not failed:
      self.log.info( 'Finished copying' );                                      # log some information
      self.log.info( 'Ready to process data files!' );                          # Log some info
      self.procButton.setEnabled( True );                                       # Enable the 'Process Files' button
  ##############################################################################
  def proc_files(self, *args):
    '''
    Method for processing sounding files;
      i.e., renaming and removing values where ballon is descending in
      sounding
    '''
    failed = False;                                                             # Initialize failed to False
    self.log.info( 'Processing files' );    
    files = os.listdir( self.dst_dirFull );                                     # Get list of all files in the directory
    for file in files:                                                          # Iterate over the list of files
      for key in settings.rename:                                               # Loop over the keys in the settings.rename dictionary
        if key in file:                                                         # If the key is in the source file name
          dst_file = settings.rename[key].format( self.date_str );              # Set a destination file name
          dst      = os.path.join( self.dst_dirFull, dst_file );                # Build the destination file path
          src      = os.path.join( self.dst_dirFull, file );                    # Set source file path
          self.uploadFile.append( dst );                                        # Append the file to the uploadFile list
          self.log.info( 'Moving file: {} -> {}'.format(src, dst) );            # Log some information
          os.rename( src, dst );                                                # Move the file
          if not os.path.isfile( dst ):                                         # If the renamed file does NOT exist
            self.log.error( 'There was an error renaming the file!' );          # Log an error
            failed = True;                                                      # Set failed to True
      for key in settings.convert:                                              # Loop over the keys in the settings.rename dictionary
        if key in file:                                                         # If the key is in the source file name
          dst_file = settings.convert[key].format( self.date_str );             # Set a destination file name
          self.sndDataFile = os.path.join( self.dst_dirFull, dst_file );        # Build the destination file path
          src              = os.path.join( self.dst_dirFull, file );            # Set source file path
          self.uploadFile.append( dst );                                        # Append the file to the uploadFile list
          
          self.log.info( 'Converting sounding data to SHARPpy format...' );     # Log some information
          res = iMet2SHARPpy( src, self.stationName.text(), 
            datetime = self.date, output = self.sndDataFile);
          if not res or not os.path.isfile( self.sndDataFile ):                 # If the renamed file does NOT exist
            self.sndDataFile = None;
            self.log.error( 'There was an error renaming the file!' );          # Log an error
            self.errorDialog(
              'Problem converting the sounding data to SHARPpy format!'
            );
            failed = True;                                                      # Set failed to True


    if not failed:                                                              # If failed is False
      self.log.info( 'Ready to generate sounding image!' );                     # Log some info
      self.genButton.setEnabled( True );                                        # Enable the 'Generate Sounding' button
  ##############################################################################
  def gen_sounding(self, *args):
    '''
    Method for generating the SPC-like sounding using the
    SPCWindow class of SHARPpy.
    '''
    self.log.info( 'Generating Skew-T diagram' )    
    sndDataPNG      = settings.skewT_fmt.format( self.date_str );
    self.sndDataPNG = os.path.join( self.dst_dirFull, sndDataPNG );
    failure = False    
    prof_collection, stn_id = self.__loadArchive( self.sndDataFile )
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
        self.skew.closed.connect(self.__skewAppClosed);
        self.skew.show();
        self.skew.addProfileCollection(prof_collection)
    else:
      raise exc
    dial = QtGui.QMessageBox()
    dial.setText( "Check that the image looks okay.\n If ok, click save, else click cancel")
    dial.setIcon(QtGui.QMessageBox.Question)
    dial.addButton('Cancel', QtGui.QMessageBox.RejectRole)
    save = dial.addButton('Save', QtGui.QMessageBox.YesRole)
    dial.exec_()
        
    if dial.clickedButton() == save:
      self.log.info('Saving the Skew-T to: {}'.format( self.sndDataPNG ) );
      pixmap = QtGui.QPixmap.grabWidget( self.skew )
      pixmap.save( self.sndDataPNG, 'PNG', 100)
      self.config.set('paths', 'save_img', os.path.dirname(self.sndDataPNG))
      self.uploadButton.setEnabled( True );
    else:
      self.log.critical('Skew-T save aborted! Not allowed to upload!')
    self.skew.close();

  ##############################################################################
  def ftp_upload(self, *args):
    self.log.info( 'uploading data' )    
  ##############################################################################
  def check_site(self, *args):
    self.log.info( 'Checking site' )    
  ##############################################################################
  def errorDialog( self, message ):
    QtGui.QMessageBox().critical(self, 
      "Caution!", 
      message
    );
  ##############################################################################
  def __loadArchive(self, filename):
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
  def __skewAppClosed(self):
    self.skew = None;
   