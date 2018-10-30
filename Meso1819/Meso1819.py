#!/usr/bin/env python2.7
import os, shutil, ConfigParser;

from PySide import QtCore;
from PySide import QtGui;

from Frames.dateFrame import dateFrame;    

from sharppy.viz.SPCWindow import SPCWindow
from sharppy.io.decoder import getDecoders

#############################################
class Meso1819( QtGui.QMainWindow ):
  def __init__(self, parent = None):
    QtGui.QMainWindow.__init__(self)
    self.setWindowTitle('Meso 18/19 Sounding Processor')
    self.src_dir = None;
    self.dest_dir   = None;
    self.iop_name   = None;
    self.dateFrame  = None;
    self.skew       = None;
    self.config     = ConfigParser.RawConfigParser()
    if not self.config.has_section('paths'):
      self.config.add_section( 'paths' );

    self.initUI();

  def initUI(self):
    self.iop_name   = QtGui.QLineEdit('IOP Name')
    self.dateFrame  = dateFrame( );
    sourceButton = QtGui.QPushButton('Source Directory');
    destButton   = QtGui.QPushButton('Destination Directory');

    sourceButton.clicked.connect( self.select_source );
    destButton.clicked.connect(   self.select_dest );

    self.copyButton = QtGui.QPushButton( 'Copy Files' );
    self.copyButton.clicked.connect( self.copy_files )

    self.procButton = QtGui.QPushButton( 'Process Files' );
    self.procButton.clicked.connect( self.proc_files )
    self.procButton.setEnabled(False)

    self.genButton = QtGui.QPushButton( 'Generate Sounding' );
    self.genButton.clicked.connect( self.gen_sounding )
    self.genButton.setEnabled(False)

    self.uploadButton = QtGui.QPushButton( 'FTP Upload' );
    self.uploadButton.clicked.connect( self.ftp_upload )
    self.uploadButton.setEnabled(False)
    

    grid = QtGui.QGridLayout();
    grid.setSpacing(10);
    grid.addWidget( sourceButton,    0, 0 )
    grid.addWidget( destButton,      1, 0 )
    grid.addWidget( self.iop_name,   2, 0 )
    grid.addWidget( self.dateFrame,  3, 0 )
    grid.addWidget( self.copyButton, 4, 0 )
    grid.addWidget( self.procButton, 5, 0 )
    grid.addWidget( self.genButton,  6, 0 )

    centralWidget = QtGui.QWidget()
    centralWidget.setLayout( grid );

    self.setCentralWidget(centralWidget)
#     self.run_But.pack(    padx = 5, pady = 5, fill = 'both', expand = True );

    self.show( )
  def selectDirectory(self, *args):
    dialog = QtGui.QFileDialog()
    dialog.setFileMode( QtGui.QFileDialog.Directory    )
    dialog.setOption(   QtGui.QFileDialog.ShowDirsOnly )
    dialog.exec_()


  ##############################################################################
  def select_source(self, *args):
    '''
    Method for selecting the source directory of the
    sounding data that was collected
    '''
    self.src_dir = QtGui.QFileDialog.getExistingDirectory()
    try:
      self.src_dir = os.path.realpath( self.src_dir );
    except:
      return;
  ##############################################################################
  def select_dest(self, *args):
    '''
    Method for selecting the source directory of the
    sounding data that was collected
    '''
    self.dest_dir = QtGui.QFileDialog.getExistingDirectory()
    try:
      self.dest_dir = os.path.realpath( self.dest_dir );
    except:
      return;
  ##############################################################################
  def copy_files(self, *args):
    self.procButton.setEnabled( True );
    return
    if self.dest_dir is None: return;
    if self.src_dir  is None: return;
    if self.dest_dir.text()   == '': return;                                                  # If the dest dir is empty the return
    if self.iop_name.text()   == '': return;                                                  # If there is no IOP name specified, then return
    
    dest_dir = os.path.join( self.dest_dir.text, self.iopFrame.iop_name.text() );# Build destination directory using the dest_dir and iop_name
    if not os.path.isdir( dest_dir ): os.make_dirs( dest_dir );                 # IF the dest_dir does NOT exist, then create it
    dest_dir = os.path.join( dest_dir, self.iopFrame.sound_name.text() );       # Append the sound_name to the dest_dir


#     shutil.copy2( src_dir, dest_dir );                                          # Copy all data from the source directory to the dest_dir

  ##############################################################################
  def proc_files(self, *args):
    print( 'processing' )    
    self.genButton.setEnabled( True );
  ##############################################################################
  def gen_sounding(self, *args):
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
    
    profs = dec.getProfiles()
    stn_id = dec.getStnId()
    
    return profs, stn_id
################################################################################
if __name__ == "__main__":
  import sys;
  qt_app = QtGui.QApplication( sys.argv )
  inst = Meso1819( );

  qt_app.exec_();