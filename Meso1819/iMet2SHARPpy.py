#!/usr/bin/env python
import numpy as np

#===============================================================================================================
#
#  Python script to convert ULM iMet sounding files to SHARPpy format
#
#===============================================================================================================


#==============================================================================================================
#
# Convert sounding
#
#==============================================================================================================
def iMet2SHARPpy( filename, stationID, time = None, datetime = None, output = None, skip_header = 3 ):
  if time is None and datetime is None:
    return False;
  elif time is None:
    time = datetime.strftime('%H%M');
  try:
    DAT = np.genfromtxt(filename, skip_header = skip_header)
  except:
    with open(filename, 'r') as fid:
      DAT = fid.readlines();                                     # Read in all the data
    DAT = [ d.rstrip().split() for d in DAT[skip_header:] ];     # Strip carriage returns and split on spaces for each line beyond header
    DAT = np.array( DAT, dtype = float );                        # Convert data to float
  pres = DAT[:,0]
  hght = DAT[:,1]
  T    = DAT[:,2]
  Td   = DAT[:,3]
  wdir = DAT[:,4]
  wspd = DAT[:,5]
  
  if datetime is None:
    year  = filename[2:4]
    month = filename[4:6]
    day   = filename[6:8]
  else:
    year  = datetime.strftime('%y');
    month = datetime.strftime('%m');
    day   = datetime.strftime('%d');
  if output is None:
    fout = open(year + month + day + time + "_SHARPpy", "wt")
  else:
    fout = open(output, "w")
  
  fout.write("%TITLE%\n")
  fout.write(stationID + " " + year + month + day + "/" + time + "\n\n");
  fout.write("LEVEL  HGHT  TEMP  DWPT WDIR  WSPD\n")
  fout.write("----------------------------------\n")
  fout.write("%RAW%\n")
  n     = 0
  mhght = hght[0]; # Set the maximum height reached by the ballon
  while n <= len(pres)-1:
    if hght[n] > mhght:
      mhght = hght[n]; # Update the maximum height reached
      if wdir[n] == 360.0: wdir[n] = 0.0
      fout.write("%s, %s, %s, %s, %s, %s\n" %(pres[n], hght[n], T[n], Td[n], wdir[n], wspd[n]))
    n=n+1
  fout.write("%END%\n");
  return True

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
  
  #==============================================================================================================
  #
  # Command line arguments
  #
  #==============================================================================================================
  
  usage  = "usage: %prog [options] arg"
  parser = OptionParser(usage)
  parser.add_option( "--filename",      dest="filename",      type="string", help="iMet sounding file name")
  parser.add_option( "--stationID",     dest="stationID",     type="string", help="3 digit station ID")
  parser.add_option( "--time",          dest="time",          type="string", help="time of launch in UTC")
  
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
  iMet2SHARPpy( options.filename, options.stationID, options.time );