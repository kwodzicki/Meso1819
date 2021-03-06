import logging
from logging.handlers import RotatingFileHandler
import os, shutil, time, webbrowser;
import numpy as np;
from datetime import datetime;
from threading import Thread, Event;

from PySide.QtGui import QMainWindow, QWidget, QFileDialog, QPixmap, QLabel;
from PySide.QtGui import QLineEdit, QPushButton, QGridLayout;
from PySide.QtCore import Qt, QTimer, Signal, Slot;

# Imports for SHARPpy
try:
  import ConfigParser;
except:
  import configparser as ConfigParse;
from utils.async import AsyncThreads
from sharppy.viz.SPCWindow import SPCWindow
from sharppy.io.spc_decoder import SPCDecoder;

# Local imports
from iMet2SHARPpy import iMet2SHARPpy;
from version import __version__;
from ftpUpload import ftpUpload;
from widgets import QLogger, dateFrame, indicator;
from messageBoxes import criticalMessage, saveMessage, confirmMessage;
import settings;

# Set up some directory paths
_home     = os.path.expanduser('~');
_desktop  = os.path.join( _home, 'Desktop' );
_logfile  = os.path.join( _desktop, 'Meso1819_Gui.log' )
_logsize  = 1024**2
_logcount = 1
#############################################
class Meso1819Gui( QMainWindow ):
  timeCheck = Signal();                                                         # Signal for time checking; used if the user tries to create Skew-T before the request sounding time actually happens; i.e., sounding date is in future
  def __init__(self, parent = None):
    QMainWindow.__init__(self);                                                 # Initialize the base class
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
    self.ftpInfo     = None;                                                    # Set attribute for ftp info
    self.ranFTP      = False;                                                   # Boolean to check if FTP uploading has been tried
    self.config      = ConfigParser.RawConfigParser();                          # Initialize a ConfigParser; required for the SPCWidget
    self.timeCheck.connect( self.on_timeCheck );                                # Connect on_timeCheck method to the timeCheck signal
    if not self.config.has_section('paths'):                                    # If there is no 'paths' section in the parser
      self.config.add_section( 'paths' );                                       # Add a 'paths' section to the parser
    self.log = logging.getLogger( __name__ );                                   # Get a logger
    rfh = RotatingFileHandler(_logfile,maxBytes=_logsize,backupCount=_logcount);# Create rotating file handler
    rfhFMT = logging.Formatter( '%(asctime)s - ' + settings.log_fmt );          # Logger format
    rfh.setFormatter( rfhFMT )
    rfh.setLevel( logging.DEBUG );                                              # Set log level to debug
    self.log.addHandler( rfh );                                                 # Add handler to main logger
    self.initUI();                                                              # Run method to initialize user interface
  ##############################################################################
  def initUI(self):
    '''
    Method to setup the buttons/entries of the Gui
    '''
    self.dateFrame    = dateFrame( );                                           # Initialize the dateFrame
    self.iopLabel     = QLabel('IOP Number');                                   # Initialize Entry widget for the IOP name
    self.iopName      = QLineEdit();                                            # Initialize Entry widget for the IOP name
    self.stationLabel = QLabel('Station Name');                                 # Initialize Entry widget for the IOP name
    self.stationName  = QLineEdit();                                            # Initialize Entry widget for the IOP name
    self.sourceButton = QPushButton('Source Directory');                        # Initialize button for selecting the source directory
    self.destButton   = QPushButton('Destination Directory');                   # Initialize button for selecting the destination directory
    self.sourcePath   = QLineEdit('');                                          # Initialize entry widget that will display the source directory path
    self.destPath     = QLineEdit('');                                          # Initialize entry widget that will display the destination directory path
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

    self.copyButton = QPushButton( 'Copy Files' );                              # Create 'Copy Files' button
    self.copyButton.clicked.connect( self.copy_files );                         # Set method to run when 'Copy Files' button is clicked
    self.copyButton.setEnabled(False);                                          # Set enabled state to False; cannot click until after the source and destination directories set
    self.copySucces = indicator();                                              # Initialize an indictor that will appear when the copy complete successfuly
    self.copySucces.hide();

    self.procButton = QPushButton( 'Process Files' );                           # Create 'Process Files' button
    self.procButton.clicked.connect( self.proc_files );                         # Set method to run when 'Process Files' button is clicked
    self.procButton.setEnabled(False);                                          # Set enabled state to False; cannot click until after 'Copy Files' completes
    self.procSucces = indicator();                                              # Initialize an indictor that will appear when the processing complete successfuly
    self.procSucces.hide();

    self.genButton = QPushButton( 'Generate Sounding' );                        # Create 'Generate Sounding' button
    self.genButton.clicked.connect( self.gen_sounding );                        # Set method to run when 'Generate Sounding' button is clicked
    self.genButton.setEnabled(False);                                           # Set enabled state to False; cannot click until after 'Process Files' completes
    self.genSucces = indicator();                                               # Initialize an indictor that will appear when the sounding generation complete successfuly
    self.genSucces.hide();

    self.uploadButton = QPushButton( 'FTP Upload' );                            # Create 'FTP Upload' button
    self.uploadButton.clicked.connect( self.ftp_upload );                       # Set method to run when 'FTP Upload' button is clicked
    self.uploadButton.setEnabled(False);                                        # Set enabled state to False; cannot click until after 'Generate Sounding' completes
    self.uploadSucces = indicator();                                            # Initialize an indictor that will appear when the ftp upload complete successfuly
    self.uploadSucces.hide();

    self.checkButton = QPushButton( 'Check website' );                          # Create 'Check website' button
    self.checkButton.clicked.connect( self.check_site );                        # Set method to run when 'Check website' button is clicked
    self.checkButton.setEnabled(False);                                         # Set enabled state to False; cannot click until after 'FTP Upload' completes

    self.resetButton = QPushButton( 'Reset' );                                  # Create 'Check website' button
    self.resetButton.clicked.connect( self.reset_values );                      # Set method to run when 'Check website' button is clicked
    
    versionLabel = QLabel( 'version: {}'.format(__version__) );                 # Version label
    versionLabel.setAlignment( Qt.AlignHCenter );                               # Set alignment to center
    log_handler  = QLogger( );                                                  # Initialize a QLogger logging.Handler object
    logging.getLogger('Meso1819').addHandler( log_handler );                    # Get the Meso1819 root logger and add the handler to it

    grid = QGridLayout();                                                       # Initialize grid layout
    grid.setSpacing(10);                                                        # Set spacing to 10
    for i in range(4): 
      grid.setColumnStretch(i,  0);                                             # Set column stretch for ith column
      grid.setColumnMinimumWidth(i,  60);                                       # Set column min width for ith column
    grid.setColumnStretch(4,  0);                                               # Set column stretch for 5th column
    grid.setColumnMinimumWidth(4,  20);                                         # Set column min width for 5th column

    grid.setRowStretch(1,  0);                                                  # Set column stretch for 5th column
    grid.setRowStretch(3,  0);                                                  # Set column stretch for 5th column
    grid.setRowMinimumHeight(1,  25);                                           # Set column min width for 5th column
    grid.setRowMinimumHeight(3,  25);                                           # Set column min width for 5th column
    
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
    grid.addWidget( self.copySucces,    7, 4, 1, 1 );                           # Place a widget in the grid
    grid.addWidget( self.procButton,    8, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.procSucces,    8, 4, 1, 1 );                           # Place a widget in the grid
    grid.addWidget( self.genButton,     9, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.genSucces,     9, 4, 1, 1 );                           # Place a widget in the grid
    grid.addWidget( self.uploadButton, 10, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.uploadSucces, 10, 4, 1, 1 );                           # Place a widget in the grid
    grid.addWidget( self.checkButton,  11, 0, 1, 4 );                           # Place a widget in the grid
    grid.addWidget( self.resetButton,  12, 0, 1, 4 );                           # Place a widget in the grid

    grid.addWidget( log_handler.frame, 0, 6, 13, 1);
    grid.addWidget( versionLabel, 20, 0, 1, 7)
    centralWidget = QWidget();                                                  # Create a main widget
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
    src_dir = QFileDialog.getExistingDirectory( dir = _desktop );               # Open a selection dialog
    self.src_dir = None if src_dir == '' else src_dir;                          # Update the src_dir attribute based on the value of src_dir

    if self.src_dir is None:                                                    # If the src_dir attribute is None
      self.log.warning( 'No source directory set' );                            # Log a warning
      self.reset_values( noDialog = True );                                     # Reset all the values in the GUI with no confirmation dialog
    else:                                                                       # Else
      self.sourcePath.setText( src_dir );                                       # Set the sourcePath label text
      self.sourcePath.show();                                                   # Show the sourcePath label
      self.sourceSet.show();                                                    # Show the sourceSet icon
      if self.dst_dir is not None:                                              # If the dst_dir attribute is not None
        self.copyButton.setEnabled( True );                                     # Set the 'Copy Files' button to enabled
        self.reset_values(noDialog = True, noSRC = True, noDST = True);         # Reset all values excluding the src AND dst directory
      else:
        self.reset_values(noDialog = True, noSRC = True);                       # Reset all values excluding the src directory

  ##############################################################################
  def select_dest(self, *args):
    '''
    Method for selecting the destination directory of the
    sounding data that was collected
    '''
    self.log.info('Setting the destination directory')
    dst_dir = QFileDialog.getExistingDirectory( dir = _desktop);                # Open a selection dialog
    self.dst_dir = None if dst_dir == '' else dst_dir;                          # Update the dst_dir attribute based on the value of dst_dir
                                                                                
    if self.dst_dir is None:                                                    # If the dst_dir attribute is None
      self.log.warning( 'No destination directory set' )                        # Log a warning
      self.reset_values( noDialog = True )                                      # Reset all the values in the GUI with no confirmation dialog
    else:                                                                       # Else
      if 'IOP' in os.path.basename( self.dst_dir ).upper():                     # If an IOP directory was selected
        self.log.debug('Moved IOP# from directory path as it is append later'); # Log some debugging information
        self.dst_dir = os.path.dirname( self.dst_dir );                         # Remove the IOP directory from the destination directory
      self.destSet.show( );                                                     # Set the destPath label text
      self.destPath.setText( self.dst_dir )                                     # Show the destPath label
      self.destPath.show()                                                      # Show the destSet icon
      if self.src_dir is not None:                                              # If the src_dir attribute is not None
        self.copyButton.setEnabled( True );                                     # Set the 'Copy Files' button to enabled
        self.reset_values(noDialog = True, noSRC = True, noDST = True);         # Reset all values excluding the src AND dst directory
      else:
        self.reset_values(noDialog = True, noDST = True);                       # Reset all values excluding the dst directory
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

    if self.iopName.text() == '':
      self.log.error( 'IOP Number NOT set!!!' )
      criticalMessage( "Must set the IOP Number!!!" ).exec_();
      return
    if self.stationName.text() == '':
      self.log.error( 'Station Name NOT set!!!' )
      criticalMessage( "Must set the Station Name!!!" ).exec_();
      return

    # Main copying code
    failed = False;                                                             # Initialize failed to False    
    self.__init_ftpInfo();                                                      # Initialize ftpInfo attribute using method
    self.date, self.date_str = self.dateFrame.getDate( );                       # Get datetime object and date string as entered in the gui
    if self.date is None: return;                                               # If the date variable is set to None
    self.dst_dirFull  = os.path.join( 
      self.dst_dir, 'IOP'+self.iopName.text(), self.date_str
    );                                                                          # Build destination directory using the dst_dir, iopName, and date string
    if not os.path.isdir( self.dst_dirFull ):                                   # If the output directory does NOT exist
      self.log.info( 'Creating directory: ' + self.dst_dirFull );               # Log some information
      os.makedirs( self.dst_dirFull );                                          # IF the dst_dir does NOT exist, then create it
    else:                                                                       # Else, the directory exists, so check to over write
      dial = confirmMessage( 
        "The destination directory exists!\n" + \
        "Do you want to overwrite it?\n\n" + \
        "YOU CANNOT UNDO THIS ACTION!!!" 
      );
      dial.exec_();                                                             # Generate the message window
      if dial.check():
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
          failed = True;                                                        # Set failed to True
          break;                                                                # Break the for loop
    if not failed:
      self.log.info( 'Finished copying' );                                      # log some information
      self.log.info( 'Ready to process data files!' );                          # Log some info
      self.copySucces.show();                                                   # Show green light next to the 'Copy Files' button to indicate that step is complete
      self.procButton.setEnabled( True );                                       # Enable the 'Process Files' button
    else:                                                                       # Else, something went wrong
      criticalMessage(
        "Something went wrong!\n\n" + \
        "There was an error copying a data file.\n" + \
        "Please check the logs and directories to see what happened."
      ).exec_(); 

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
    rename_status  = dict.fromkeys( settings.rename.keys(),  False);            # Status of file renaming
    process_status = dict.fromkeys( settings.convert.keys(), False);            # Status of file processing

    for file in files:                                                          # Iterate over the list of files
      for key in settings.rename:                                               # Loop over the keys in the settings.rename dictionary
        if key in file:                                                         # If the key is in the source file name
          rename_status[key] = True;                                            # Add rname status as True
          dst_file = settings.rename[key].format( self.date_str );              # Set a destination file name
          dst      = os.path.join( self.dst_dirFull, dst_file );                # Build the destination file path
          src      = os.path.join( self.dst_dirFull, file );                    # Set source file path
#           self.uploadFiles.append( dst );                                     # Append the file to the uploadFile list
          self.log.info( 'Moving file: {} -> {}'.format(src, dst) );            # Log some information
          os.rename( src, dst );                                                # Move the file
          if not os.path.isfile( dst ):                                         # If the renamed file does NOT exist
            self.log.error( 'There was an error renaming the file!' );          # Log an error
            failed = True;                                                      # Set failed to True
      
      file_found = False;                                                       # Flag for in the file to process is found!
      for key in settings.convert:                                              # Loop over the keys in the settings.rename dictionary
        if key in file:                                                         # If the key is in the source file name
          process_status[key] = True;                                           # Set to true if the file is found
          dst_file = settings.convert[key].format( self.date_str );             # Set a destination file name
          self.sndDataFile = os.path.join( self.dst_dirFull, dst_file );        # Build the destination file path
          src              = os.path.join( self.dst_dirFull, file );            # Set source file path
#           self.uploadFiles.append( dst );                                     # Append the file to the uploadFile list
          
          self.log.info( 'Converting sounding data to SHARPpy format...' );     # Log some information
          res = iMet2SHARPpy( src, self.stationName.text().upper(), 
            datetime = self.date, output = self.sndDataFile);                   # Run function to convert data to SHARPpy format
          if res and os.path.isfile( self.sndDataFile ):                        # If function returned True and the output file exists
            for key in self.ftpInfo:                                            # Iterate over keys in ftpInfo attribute
              self.ftpInfo[key]['files'].append( self.sndDataFile );            # Append sounding data file path to files key in ftpInfo dictionary
          else:
            failed = True;                                                      # Set failed to True
            self.sndDataFile = None;                                            # if the function failed to run OR the output file does NOT exist
            self.log.error( 'There was an error creating SHARPpy file!' );      # Log an error
            criticalMessage(
              'Problem converting the sounding data to SHARPpy format!'
            ).exec_();                                                          # Generate critical error message box
    
    if not all( rename_status.values() ):
      failed = True;
      self.log.error( 'There was an error renaming one or more files!' );       # Log an error
      criticalMessage(
        'Problem renaming one or more files!'
      ).exec_();                                                          # Generate critical error message box

    if not all( process_status.values() ):
      failed = True;
      self.log.error( 'There was an error converting one or more files to SHARPpy format!' );       # Log an error
      criticalMessage(
        'Problem converting one or more files to SHARPpy format!'
      ).exec_();                                                          # Generate critical error message box

    if not failed:                                                              # If failed is False
      self.procSucces.show();                                                   # Show green light next to the 'Process Files' button to indicate that step is complete
      if self.date <= datetime.utcnow():                                        # If the date for the sound is NOT in the future
        self.timeCheck.emit();                                                  # Emit signal to activate the 'Generate Sounding' button
      else:                                                                     # Else, date for sounding IS in the future
        dt  = self.date - datetime.utcnow();                                    # Compute the current time difference between the sounding and utcnow
        msg = ['Date requested is in the future!', 
               'Sounding generation disabled until requested sounding time',
               'Wait time remaining {}'.format( str(dt) ) ];                    # List that contains message for the logger
        self.log.warning( '\n'.join(msg) );                                     # Log the message as a warning
        criticalMessage(
          'The data processing has completed!\n\n' + \
          'However, the requested date/time for the\n' + \
          'sounding is in the future!\n\n' +\
          'The \'Generate Sounding\' button will activate\n' + \
          'when the current time is after the requested time!'
        ).exec_();                                                              # Generate critical error message box
        dt = (int( dt.total_seconds() ) + 2) * 1000;                            # Get total time between now and future time, add 2 seconds, convert to integer, then conver to milliseconds
        QTimer.singleShot( dt, self._timeCheck );                               # Run single shot timer thread for the _timeCheck method, waiting dt milliseconds before running
  ##############################################################################
  def gen_sounding(self, *args):
    '''
    Method for generating the SPC-like sounding using the
    SPCWindow class of SHARPpy.
    '''
    self.log.info( 'Generating Skew-T diagram' );                               # Log some information
    sndDataPNG      = settings.skewT_fmt.format( self.date_str );               # Set the name for the skewT file using the settings.skew_T_fmt string
    self.sndDataPNG = os.path.join( self.dst_dirFull, sndDataPNG );             # Set the sndDataPNG attribute using the dst_dirFull attribute and sndDataFile variable

    save_msg = "Check that the image looks okay.\n " + \
      "If ok, click save, else click cancel";                                   # Confirmation message for the save dialog for Skew-T; will update if cannot save Skew-T due to issue in SHARPpy
    sharppy_bug = False;                                                        # Flag for if sharppy bug encountered
    try:                                                                        # Try to...
      decoder = SPCDecoder( self.sndDataFile );                                 # Decode the sounding file using the SPCDecoder
      profile = decoder.getProfiles();                                          # Get the profiles from the file
      stn_id  = decoder.getStnId();                                             # Get the station id from the file
    except:                                                                     # On exception
      criticalMessage( 
        "There was an error loading the sounding data\n\n"
      ).exec_();                                                                # Initialize and display critical error dialog
      return;                                                                   # Return from method
    model     = "Archive";                                                      # Set model to 'Archive'; not sure why but was in the SHARPpy full_gui.py 
    disp_name = stn_id;                                                         # Set the display name to the station ID from the sounding data file
    run       = profile.getCurrentDate();                                       # Set the run to the current date from the sounding data
    profile.setMeta('model', model);                                            # Set the model in the sounding data
    profile.setMeta('loc',   disp_name);                                        # Set the display name in the sounding data
    profile.setMeta('run',   run);                                              # Set the run in the sounding data
    
    if not profile.getMeta('observed'):                                         # If it's not an observed profile
      profile.setAsync( AsyncThreads(2, debug) );                               # Generate profile objects in background. Not sure why works but in SHARPpy full_gui.py
    
    self.log.debug('Generating SHARPpy window')
    if self.skew is None:                                                       # If there is no skew window setup; there should never be...
      self.skew = SPCWindow(cfg=self.config);                                   # Initialize a new SPCWindow object
      self.skew.closed.connect(self.__skewAppClosed);                           # Connect the closed method to the __skewAppClosed private method
      self.skew.addProfileCollection(profile);                                  # Add the profile data to the SPCWindow object
      try:
        self.skew.show();                                                         # Show the window
      except:
        sharppy_bug = True;
        self.log.warning("SHARPpy didn't like that sounding very much!")
        save_msg = "Congradulations!\n\n"   + \
          "You just found a bug in SHARPpy.\n" + \
          "There is nothing we can about this. No Skew-T can be created.\n" + \
          "Just click 'Save' and continue with the uploading";
    dial = saveMessage( save_msg );                                             # Set up save message pop-up
    dial.exec_();                                                               # Display the save message pop-up
    if dial.check():                                                            # If clicked save
      if not sharppy_bug:                                                       # If the SHARPpy bug did NOT occur
        self.ftpInfo['ucar']['files'].append( self.sndDataPNG );                # Append the SHARPpy image file name to the ftpInfo['ucar']['files'] list
        self.log.info('Saving the Skew-T to: {}'.format( self.sndDataPNG ) );   # Log some information
        pixmap = QPixmap.grabWidget( self.skew );                               # Grab the image from the skew T window
        pixmap.save( self.sndDataPNG, 'PNG', 100);                              # Save the image
        self.config.set('paths', 'save_img', os.path.dirname(self.sndDataPNG)); # Add image path to the config object

      self.log.debug( 'Files to upload to UCAR: {}'.format( 
        ', '.join(self.ftpInfo['ucar']['files']) ) )
      self.genSucces.show();                                                    # Show green light next to the 'Generate Sounding' button to indicate that step is complete
      self.uploadButton.setEnabled( True );                                     # Enable the upload button
    else:                                                                       # Else
      self.log.critical('Skew-T save aborted! Not allowed to upload!');         # Log an error
    try:
      self.skew.close();                                                        # Close the skew T window
    except:
      pass;
  ##############################################################################
  def ftp_upload(self, *args):
    if self.ranFTP:
      self.log.info( 'You already ran this step!' );
      criticalMessage( "You already tried to upload to FTP" ).exec_();          # Initialize confirmation for quitting
      return;
    self.ranFTP = True;                                                         # Set ran FTP to True
    for key in self.ftpInfo:                                                    # Iterate over all keys in the ftpInfo dictionary
      self.log.info( 'Uploading data to: {}'.format(self.ftpInfo[key]['url']) );# Log some info
      try:                                                                      # Try to...
        ftp = ftpUpload( self.ftpInfo[key]['url'] );                            # Set up and FTP instance
      except:                                                                   # On exception...
        self.log.critical( 
          'Error initializing the FTP upload: {}'.format(
            self.ftpInfo[key]['url']
          )
        );                                                                      # Log a critical error
      else:                                                                     # Else...
        self.ftpInfo[key]['upload'] = ftp.uploadFiles(
          self.ftpInfo[key]['dir'], 
          self.ftpInfo[key]['files'], 
          user   = self.ftpInfo[key]['user'],
          passwd = self.ftpInfo[key]['passwd'],
        );                                                                      # Attempt to upload the files
      if not self.ftpInfo[key]['upload']:                                       # If one or more files failed to upload
        msg = 'FAILED!!! Upload to {} NOT successful';                          # Formatter for error message
        self.log.critical( msg.format( self.ftpInfo[key]['url'] ) );            # Log a critical error
        criticalMessage( 
          "Something went wrong!\n\n" + \
          "There was an error uploading one or more files to the FTP.\n\n"  + \
          "FTP Address: {}\n\n".format( self.ftpInfo[key]['url'] )          + \
          "Check the logs to determine which file(s) failed to upload.\n\n" + \
          "YOU MUST MANUALLY UPLOAD ANY FILES THAT FAILED!!!"
        ).exec_();
      else:
        self.log.info( 'Data upload successful!' );
    if self.ftpInfo['ucar']['upload']:                                          # If the upload to UCAR was a success
      self.uploadSucces.show();                                                 # Show green light next to the 'FTP Upload' button to indicate that step is complete
      self.checkButton.setEnabled(True)
  ##############################################################################
  def check_site(self, *args):
    self.log.info( 'Checking site' )    
    webbrowser.open( settings.url_check )
  ##############################################################################
  def reset_values(self, noDialog = False, noSRC = False, noDST = False):
    '''
    Method to reset all the values in the GUI
    Keywords:
       noDialog  : Set to true to disable the checking dialog
       noSRC     : Set to true so that all values BUT source directory info are cleared
       noDST     : Set to true so that all values BUT destination directory info are cleared
       
       Setting both noSRC and noDST will exclude the two directories
    '''
    check = False;                                                              # Dialog check value initialize to False
    if not noDialog:                                                            # If noDialog is False
      dial = confirmMessage( 'Are you sure you want to reset all values?' );    # Initialize confirmation dialog
      dial.exec_();                                                             # Display the confirmation dialog
      check = dial.check();                                                     # Check which button selected
    if check or noDialog:                                                       # If the check is True or noDialog is True
      self.log.debug( 'Resetting all values!' );                                # Log some information
      if not noSRC or not noDST:                                                # If noSRC is False OR noDST is false
        self.copyButton.setEnabled( False );                                    # Set enabled state to False; cannot click until after the source and destination directories set
      self.procButton.setEnabled(   False );                                    # Set enabled state to False; cannot click until after 'Copy Files' completes
      self.genButton.setEnabled(    False );                                    # Set enabled state to False; cannot click until after 'Process Files' completes
      self.uploadButton.setEnabled( False );                                    # Set enabled state to False; cannot click until after 'Generate Sounding' completes
      self.checkButton.setEnabled(  False );                                    # Set enabled state to False; cannot click until after 'FTP Upload' completes
      
      self.copySucces.hide();
      self.procSucces.hide();
      self.genSucces.hide()
      self.uploadSucces.hide();
  
      if not noSRC:                                                             # If the noSRC keyword is NOT set
        self.sourcePath.hide();                                                 # Hide the source directory path
        self.sourceSet.hide();                                                  # Hide the source directory indicator
      if not noDST:                                                             # If the noDST keyword is NOT set
        self.destPath.hide();                                                   # Hide the destination directory path
        self.destSet.hide();                                                    # Hide the destination directory indicator
  
      self.dateFrame.resetDate();                                               # Reset all the dates
      self.iopName.setText(     '' );                                           # Initialize Entry widget for the IOP name
      self.stationName.setText( '' );                                           # Initialize Entry widget for the IOP name
      self.ranFTP = False;                                                      # Reset ranFTP to False on reset
      self.__reset_ftpInfo();
  ##############################################################################
  def closeEvent(self, event):
    '''
    Method to override closeEvent handler to add a confirmation dialog
    to application quit
    '''
    dial = confirmMessage( "Are you sure you want to quit?" );                  # Initialize confirmation for quitting
    dial.exec_();                                                               # Generate the message window
    if dial.check():                                                            # If user selected yes on dialog
      event.accept();                                                           # Accept the event and close the GUI
    else:                                                                       # Else
      event.ignore();                                                           # Ignore the event; i.e., keep GUI open
  ##############################################################################
  @Slot()
  def on_timeCheck(self):
    self.log.info( 'Ready to generate sounding image!' );                       # Log some info
    self.genButton.setEnabled( True );                                          # Enable the 'Generate Sounding' button
  ##############################################################################
  def _timeCheck(self):
    if self.date <= datetime.utcnow():                                          # Check requested date is in the future AND the timeEvent is NOT set
      self.timeCheck.emit();                                                    # Emit a signal to enable the 'Generate Sounding' button
    else:                                                                       # Else, date is still in future...
      QTimer.singleShot( 1000, self._timeCheck );                               # Wait one second and call this method again
  ##############################################################################
  def __skewAppClosed(self):
    self.skew = None;
  ##############################################################################
  def __init_ftpInfo(self):
    self.ftpInfo = {'ucar' : settings.ucar_ftp, 
                    'noaa' : settings.noaa_ftp};
    for key in self.ftpInfo:
      self.ftpInfo[key]['files']  = [];
      self.ftpInfo[key]['upload'] = False;
  ##############################################################################
  def __reset_ftpInfo(self):
    self.ftpInfo = None;