#!/usr/bin/env python
import logging;
import numpy as np;

#===============================================================================================================
#
#  Python script to convert ULM iMet sounding files to SHARPpy format
#
#===============================================================================================================

def iMet2SHARPpy( filename, stationID, time = None, datetime = None, output = None, skip_header = 3 ):
  '''
  Name:
     iMet2SHARPpy
  Purpose
     A python function to convert iMet sounding files to 
     SHARPpy format for plotting.
  Inputs:
     filename  : Path to the iMet data file. Assumes year, month, 
                  and day are in the file name.
     stationID : Station ID for the file; 
                   i.e., KCLL for College Station, TX
  Outputs:
     Returns True if conversion successful, False otherwise
  Keywords:
     time        : String containing time of sounding with format HHMM
     datetime    : A datetime object containing the date and time of the
                     sounding; i.e., datetime(yyyy, mm, dd, hh, mn)
     output      : Full path to the output file. Default is to output to
                     YYYYMMDDhh_SHARPpy file
     skip_header : Number of header lines in the iMet file to skip.
                     Default is 3
  '''
  log = logging.getLogger( __name__ );                                          # Initialize logger for the function
  if time is None and datetime is None:                                         # If time is None AND datetime is None
    log.warning('No time or datetime object input!');                           # Log a warning
    return False;                                                               # Return False
  elif time is None:                                                            # Elif time is None; then datetime must NOT be None
    time = datetime.strftime('%H%M');                                           # Get hour/minute from datetime in format HHMM

  log.debug('Reading input file');                                              # Log some debugging information
  try:                                                                          # Try to...
    DAT = np.genfromtxt(filename, skip_header = skip_header);                   # Us the genfromtxt numpy function to read in the data file
  except:                                                                       # On exception...
    with open(filename, 'r') as fid:                                            # Open the file for reading
      DAT = fid.readlines();                                                    # Read in all the data
    DAT = [ d.rstrip().split() for d in DAT[skip_header:] ];                    # Strip carriage returns and split on spaces for each line beyond header
    DAT = np.array( DAT, dtype = float );                                       # Convert data to float

  pres = DAT[:,0];                                                              # Get the pressure data from the DAT numpy array
  hght = DAT[:,1];                                                              # Get the height data from the DAT numpy array
  T    = DAT[:,2];                                                              # Get the temperature data from the DAT numpy array
  Td   = DAT[:,3];                                                              # Get the dew point data from the DAT numpy array
  wdir = DAT[:,4];                                                              # Get the wind direction data from the DAT numpy array
  wspd = DAT[:,5];                                                              # Get the wind speed data from the DAT numpy array
  
  if datetime is None:                                                          # If datetime is None; i.e., not input
    year  = filename[2:4];                                                      # Set the year based on input filename
    month = filename[4:6];                                                      # Set the month based on input filename
    day   = filename[6:8];                                                      # Set the day based on input filename
  else:                                                                         # Else, use datetime object to...
    year  = datetime.strftime('%y');                                            # Set the year
    month = datetime.strftime('%m');                                            # Set the month
    day   = datetime.strftime('%d');                                            # Set the day

  log.debug('Opening output file');                                             # Log some debugging info
  if output is None:                                                            # If output is None; i.e., not specified
    fout = open(year + month + day + time + "_SHARPpy", "wt");                  # Open the default output file for writing
  else:                                                                         # Else
    fout = open(output, "w");                                                   # Open the user specified output file for writing
  
  log.debug('Writing header information');                                      # Log some debugging info
  fout.write("%TITLE%\n");                                                      # Write first line of header information to the SHARPpy file
  fout.write(stationID + " " + year + month + day + "/" + time + "\n\n");       # Write second line of header information to the SHARPpy file
  fout.write("LEVEL  HGHT  TEMP  DWPT WDIR  WSPD\n");                           # Write third line of header information to the SHARPpy file
  fout.write("----------------------------------\n");                           # Write fourth line of header information to the SHARPpy file
  fout.write("%RAW%\n");                                                        # Write last line of header information to the SHARPpy file

  n     =     0;                                                                # Set data line number counter to zero                           
  nrm   =     0;                                                                # Set number of lines removed from balloon descent counter to zero
  mhght = -9999.0;                                                              # Set the maximum height reached by the ballon to large negative number
  fmt   = "%s, %s, %s, %s, %s, %s\n";                                           # Formation for data lines in the SHARPpy file
  while n <= len(pres)-1:                                                       # Iterate over all data lines
    if hght[n] > mhght:                                                         # If the height of the balloon at line n is greater than the maximum height reached by the balloon
      mhght = hght[n];                                                          # Set maximum height to the current height
      if wdir[n] == 360.0: wdir[n] = 0.0;                                       # If the wind direction = 360, set to zero
      fout.write(fmt % (pres[n], hght[n], T[n], Td[n], wdir[n], wspd[n]));      # Write the data to the output file
    else:                                                                       # Else
      nrm = nrm + 1;                                                            # Increment the line(s) removed counter
    n = n+1;                                                                    # Increment the data line number counter
  fout.write("%END%\n");                                                        # Write footer to the SHARPpy file
  fout.close();                                                                 # Close the output file
  if nrm > 0:                                                                   # If number of lines removed is greater than zero
    log.warning( 'Balloon descent(s) detected, {} lines removed'.format(nrm) ); # Log a warning
  log.debug('Finished converting file');                                        # Log some info
  return True;                                                                  # Return True

#==============================================================================================================
#
# Command line arguments
#
#==============================================================================================================
if __name__ == "__main__":
  #
  # System imports
  #  import sys
  from optparse import OptionParser
  # Extra help
  
  myhelp = """\n
  
              A general run script to convert iMet sounding files to SHARPpy format.
  
              Usage examples:
   
              python iMet2SHARPpy.py --filename 20160202_TSPOTINT.txt --stationID ULM --time 1830
                                                                              
           """
  usage  = "usage: %prog [options] arg"
  parser = OptionParser(usage)
  parser.add_option( "--filename",  dest="filename",  type="string", help="iMet sounding file name")
  parser.add_option( "--stationID", dest="stationID", type="string", help="3 digit station ID")
  parser.add_option( "--time",      dest="time",      type="string", help="time of launch in UTC")
  
  (options, args) = parser.parse_args()
  
  # Check for proper file name, stationID, and station elevation
  if options.filename == None: 
  	print "\nERROR: File name not supplied...exiting\n"
  	sys.exit()
  else:
  	filename = options.filename
  	
  if options.stationID == None:
  	print "\nStation ID not supplied..."
  	print "Using default ULM\n"
  	stationID = "ULM"
  else:
  	stationID = options.stationID
  	
  if options.time == None:
  	print "\nTime of launch not supplied..."
  	print "Using default of 0000\n"
  	time = "0000"
  else:
  	time = options.time
  iMet2SHARPpy( filename, stationID, time );