'''
File containing setting information such as URLs for FTP site,
formatting strings for file names and logging, etc.
'''

# log_fmt  = '%(levelname)-.4s - %(message)s - %(asctime)s';
log_fmt  = '%(levelname)-.4s - %(message)s';

date_fmt  = '%Y%m%d%H%M';        # Format for datetime objects
skewT_fmt = 'upperair.TAMU_sonde.{}.College_Station_TX_skewT.png'

rename    = {
  'TEMP.txt' : 'upperair.TAMU_sonde.{}.College_Station_TX_TEMPMOBIL.txt',
}

convert = {
  'TSPOTINT.txt' : 'upperair.TAMU_sonde.{}.College_Station_TX_SHARPpy.txt',
}