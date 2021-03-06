'''
File containing setting information such as URLs for FTP site,
formatting strings for file names and logging, etc.
'''

# log_fmt  = '%(levelname)-.4s - %(message)s - %(asctime)s';
log_fmt   = '%(levelname)-.4s - %(message)s - %(name)s.%(funcName)s';
date_fmt  = '%Y%m%d%H%M';        # Format for datetime objects

# stations = {
#   'KCLL'  : {'id' : 'TAMU', 'city' : 'College Station', 'state' : 'TX'},
# };

skewT_fmt = 'upperair.TAMU_sonde.{}.College_Station_TX_skewT.png';

rename    = {
  'TEMP.txt' : 'upperair.TAMU_sonde.{}.College_Station_TX_TEMPMOBIL.txt',
};

convert = {
  'TSPOTINT.txt' : 'upperair.TAMU_sonde.{}.College_Station_TX_SHARPpy.txt',
};

url_check = 'http://catalog.eol.ucar.edu/meso18-19/upperair';

ucar_ftp = {
  'url'    : 'catalog.eol.ucar.edu',
  'user'   : 'anonymous',
  'passwd' : None,
  'dir'    : '/pub/incoming/catalog/vortexse',
};

noaa_ftp = {
  'url'    : 'awftp.fsl.noaa.gov',
  'user'   : 'anonymous',
  'passwd' : None,
  'dir'    : '/its/vortex-se/sondes',
};