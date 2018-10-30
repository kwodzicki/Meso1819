import matplotlib.pyplot as plt

from matplotlib.axes import Axes
import matplotlib.transforms as transforms
import matplotlib.axis as maxis
import matplotlib.spines as mspines
import matplotlib.path as mpath
from matplotlib.projections import register_projection

import sharppy
import sharppy.sharptab.profile as profile
import sharppy.sharptab.interp as interp
import sharppy.sharptab.winds as winds
import sharppy.sharptab.utils as utils
import sharppy.sharptab.params as params
import sharppy.sharptab.thermo as thermo

from sharppy.sharptab.profile import ConvectiveProfile;
from StringIO import StringIO;
import numpy as np;


# The sole purpose of this class is to look at the upper, lower, or total
# interval as appropriate and see what parts of the tick to draw, if any.
class SkewXTick(maxis.XTick):
    def draw(self, renderer):
        if not self.get_visible(): return
        renderer.open_group(self.__name__)

        lower_interval = self.axes.xaxis.lower_interval
        upper_interval = self.axes.xaxis.upper_interval

        if self.gridOn and transforms.interval_contains(
                self.axes.xaxis.get_view_interval(), self.get_loc()):
            self.gridline.draw(renderer)

        if transforms.interval_contains(lower_interval, self.get_loc()):
            if self.tick1On:
                self.tick1line.draw(renderer)
            if self.label1On:
                self.label1.draw(renderer)

        if transforms.interval_contains(upper_interval, self.get_loc()):
            if self.tick2On:
                self.tick2line.draw(renderer)
            if self.label2On:
                self.label2.draw(renderer)

        renderer.close_group(self.__name__)


# This class exists to provide two separate sets of intervals to the tick,
# as well as create instances of the custom tick
class SkewXAxis(maxis.XAxis):
    def __init__(self, *args, **kwargs):
        maxis.XAxis.__init__(self, *args, **kwargs)
        self.upper_interval = 0.0, 1.0

    def _get_tick(self, major):
        return SkewXTick(self.axes, 0, '', major=major)

    @property
    def lower_interval(self):
        return self.axes.viewLim.intervalx

    def get_view_interval(self):
        return self.upper_interval[0], self.axes.viewLim.intervalx[1]


# This class exists to calculate the separate data range of the
# upper X-axis and draw the spine there. It also provides this range
# to the X-axis artist for ticking and gridlines
class SkewSpine(mspines.Spine):
    def _adjust_location(self):
        trans = self.axes.transDataToAxes.inverted()
        if self.spine_type == 'top':
            yloc = 1.0
        else:
            yloc = 0.0
        left = trans.transform_point((0.0, yloc))[0]
        right = trans.transform_point((1.0, yloc))[0]

        pts  = self._path.vertices
        pts[0, 0] = left
        pts[1, 0] = right
        self.axis.upper_interval = (left, right)


# This class handles registration of the skew-xaxes as a projection as well
# as setting up the appropriate transformations. It also overrides standard
# spines and axes instances as appropriate.
class SkewXAxes(Axes):
    # The projection must specify a name.  This will be used be the
    # user to select the projection, i.e. ``subplot(111,
    # projection='skewx')``.
    name = 'skewx'

    def _init_axis(self):
        #Taken from Axes and modified to use our modified X-axis
        self.xaxis = SkewXAxis(self)
        self.spines['top'].register_axis(self.xaxis)
        self.spines['bottom'].register_axis(self.xaxis)
        self.yaxis = maxis.YAxis(self)
        self.spines['left'].register_axis(self.yaxis)
        self.spines['right'].register_axis(self.yaxis)

    def _gen_axes_spines(self):
        spines = {'top':SkewSpine.linear_spine(self, 'top'),
                  'bottom':mspines.Spine.linear_spine(self, 'bottom'),
                  'left':mspines.Spine.linear_spine(self, 'left'),
                  'right':mspines.Spine.linear_spine(self, 'right')}
        return spines

    def _set_lim_and_transforms(self):
        """
        This is called once when the plot is created to set up all the
        transforms for the data, text and grids.
        """
        rot = 30

        #Get the standard transform setup from the Axes base class
        Axes._set_lim_and_transforms(self)

        # Need to put the skew in the middle, after the scale and limits,
        # but before the transAxes. This way, the skew is done in Axes
        # coordinates thus performing the transform around the proper origin
        # We keep the pre-transAxes transform around for other users, like the
        # spines for finding bounds
        self.transDataToAxes = self.transScale + (self.transLimits +
                transforms.Affine2D().skew_deg(rot, 0))

        # Create the full transform from Data to Pixels
        self.transData = self.transDataToAxes + self.transAxes

        # Blended transforms like this need to have the skewing applied using
        # both axes, in axes coords like before.
        self._xaxis_transform = (transforms.blended_transform_factory(
                    self.transScale + self.transLimits,
                    transforms.IdentityTransform()) +
                transforms.Affine2D().skew_deg(rot, 0)) + self.transAxes


# Now register the projection with matplotlib so the user can select
# it.
register_projection(SkewXAxes)

def parseData( file ):
  with open(file, 'r') as fid:
    data = np.array( fid.read().split('\n') );
  title_idx  = np.where( data == '%TITLE%')[0][0]
  start_idx  = np.where( data == '%RAW%' )[0] + 1
  finish_idx = np.where( data == '%END%')[0]
  plot_title = data[title_idx + 1] + ' (Observed)'
  full_data  = '\n'.join(data[start_idx[0] : finish_idx[0]])
  sound_data = StringIO( full_data )
  p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, 
    delimiter=',', comments="%", unpack=True
  );
  return {'pres' : p, 
          'hght' : h,
          'tmpc' : T,
          'dwpc' : Td,
          'wdir' : wdir,
          'wspd' : wspd}


class sharppyFigure( ConvectiveProfile ):
  def __init__(self, file):
#     with open(file, 'r') as fid:
#       data = np.array( fid.read().split('\n') );
#     title_idx  = np.where( data == '%TITLE%')[0][0]
#     start_idx  = np.where( data == '%RAW%' )[0] + 1
#     finish_idx = np.where( data == '%END%')[0]
#     plot_title = data[title_idx + 1] + ' (Observed)'
#     full_data  = '\n'.join(data[start_idx[0] : finish_idx[0]])
#     sound_data = StringIO( full_data )
#     p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, 
#       delimiter=',', comments="%", unpack=True
#     );
#     ConvectiveProfile.__init__(self, 
#       profile='convective', pres=p, hght=h, tmpc=T, dwpc=Td,
#     	wdir=wdir, wspd=wspd, missing = -9999.0
#     );
    data = parseData( file );
    ConvectiveProfile.__init__(self, 
      profile='convective', missing = -9999.0, **data
    );

 
    self.fig = plt.figure(figsize=(6.5875, 6.2125));                            # Create a new figure. The dimensions here give a good aspect ratio
    self.fig.set_facecolor('black')

    ax = self.fig.add_subplot(111, projection='skewx')
    ax.set_facecolor('black')
    ax.grid(True)
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    sfcpcl  = params.parcelx( self, flag=1 ) # Surface Parcel
    fcstpcl = params.parcelx( self, flag=2 ) # Forecast Parcel
    mupcl   = params.parcelx( self, flag=3 ) # Most-Unstable Parcel
    mlpcl   = params.parcelx( self, flag=4 ) # 100 mb Mean Layer Parcel
    
    pcl = mupcl

    pmax = 1000
    pmin = 10
    dp = -10
    presvals = np.arange(int(pmax), int(pmin)+dp, dp)
    
    # plot the moist-adiabats
    for t in np.arange(-10,45,5):
        tw = []
        for p in presvals:
            tw.append(thermo.wetlift(1000., t, p))
        ax.semilogy(tw, presvals, 'k-', alpha=.2)
    # plot the dry adiabats
    for t in np.arange(-50,110,10):
        ax.semilogy(thetas(t, presvals), presvals, 'r-', alpha=.2)
    
    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dicatated by the typical meteorological plot
    ax.semilogy(self.tmpc, self.pres, 'r', lw=2)
    ax.semilogy(self.dwpc, self.pres, 'g', lw=2)
    ax.semilogy(pcl.ttrace, pcl.ptrace, 'k-.', lw=2)
    
    # An example of a slanted line at constant X
    l = ax.axvline(0, color='b', linestyle='--')
    l = ax.axvline(-20, color='b', linestyle='--')
    
    # Disables the log-formatting that comes with semilogy
    ax.yaxis.set_major_formatter(plt.ScalarFormatter())
    ax.set_yticks(np.linspace(100,1000,10))
    ax.set_ylim(1050,100)
    
    ax.xaxis.set_major_locator(plt.MultipleLocator(10))
    ax.set_xlim(-50,50)
    
def thetas(theta, presvals):
  return ((theta + thermo.ZEROCNK) / (np.power((1000. / presvals),thermo.ROCP))) - thermo.ZEROCNK