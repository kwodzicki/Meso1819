import logging;
import os;
from ftplib import FTP;

class ftpUpload( FTP ):
  def __init__(self, url):
    FTP.__init__(self, url);
    self.log = logging.getLogger(__name__);
  ################################################################
  def _login(self, user = None, passwd = None):
    try:
      self.login( user, passwd );
    except Exception as err:
      self.log.critical('Failed to login to FTP!');
      self.log.critical( 'ftplib: {}'.format(err) );                          # Log the ftplib error so know what is happening
      return False; 
    self.log.info('Logged into FTP server')
    return True; 
  ################################################################
  def _logout(self):
    try:
      self.quit( )
    except Exception as err:
      self.log.warning('Failed to log out correctly!');
      self.log.critical( 'ftplib: {}'.format(err) );                          # Log the ftplib error so know what is happening
      return False;
    self.log.info('Logged out of FTP server')
    return True;
  ################################################################
  def _cwd(self, dir):
    try:
      self.cwd( dir )
    except Exception as err:
      self.log.critical('Failed to change directory!');
      self.log.critical( 'ftplib: {}'.format(err) );                          # Log the ftplib error so know what is happening
      return False;
    self.log.info('Changed to {}'.format(dir))
    return True;

  ################################################################
  def uploadFiles(self, dir, fileList, user = None, passwd = None):
    if not self._login( user, passwd ): return False;                           # If fail to log in, return False
    if not self._cwd( dir ):                                                    # If fail to change directory
      self._logout();                                                           # Log out
      return False;                                                             # Return False
    failed = False;                                                             # Initialize failed to False
    for file in fileList:                                                       # Iterate over all files in fileList
      base = os.path.basename( file );                                          # Get the base file name
      fid  = open(file, 'rb');                                                  # Open file in binary read mode
      try:                                                                      # Try to...
        self.storbinary( 'STOR {}'.format( base ), fid );                       # Upload the file
      except Exception as err:                                                  # On error
        failed = True;                                                          # Set failed to True
        self.log.critical( 'Failed to upload file {}'.format(base) );           # Log some information
        self.log.critical( 'ftplib: {}'.format(err) );                          # Log the ftplib error so know what is happening
      else:
        self.log.info( 'Uploaded file: {}'.format( base ) );
      fid.close();                                                              # close the file
    self._logout();                                                             # Logout of the FTP
    return (not failed);                                                        # Return opposite value of failed; i.e., if all passed, failed should be False, so this return True. If one or mored failed, failed will be True and thus return False