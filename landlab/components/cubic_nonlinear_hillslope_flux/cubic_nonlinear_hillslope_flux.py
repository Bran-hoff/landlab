# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 11:15:21 2016

@author: RCGlade
"""

#Cubic hillslope flux component

from landlab import Component
import numpy as np
from landlab import INACTIVE_LINK, CLOSED_BOUNDARY

import warnings
import os

class CubicNonLinearDiffuser(Component):
    
    """
    hillslope evolution using a cubic formulation of hillslope flux derived from
    a taylor expansion of the nonlinear flux rule, following Ganti et al., 2012. 
    
    Parameters
    ----------
    grid: ModelGrid
            Landlab ModelGrid object
    linear_diffusivity: float
            Hillslope diffusivity, m**2/yr
    slope_crit: float
            Critical slope 
        
    Examples
    --------
    >>> import numpy as np
    >>> import decimal
    >>> from landlab import RasterModelGrid 
    >>> from landlab.plot.imshow import imshow_node_grid
    >>> mg = RasterModelGrid((3, 3))
    >>> z = mg.add_zeros('node', 'topographic__elevation')
    >>> initial_slope=1.0
    >>> leftmost_elev=1000.
    >>> z[:] = leftmost_elev
    >>> z[:] += (initial_slope * np.amax(mg.x_of_node)) - (initial_slope * mg.x_of_node)
    >>> mg.set_closed_boundaries_at_grid_edges(False, True, False, True)
    >>> cubicflux = CubicNonLinearDiffuser(mg, soil_transport_coefficient=0.5, slope_crit=0.1)
    >>> cubicflux.run_one_step(1.)
    >>> np.allclose(
    ...     mg.at_node['topographic__elevation'],
    ...     np.array([ 1002.,  1001.,  1000.,  1002.,  1001.,  1000.,  1002.,  1001.,
    ...     1000.]))
    True
    
    The CubicNonLinearDiffuser makes and moves soil at a rate proportional
    to slope, this means that there is a characteristic time scale for soil 
    transport and an associated stability criteria for the timestep. The 
    maximum characteristic time scale, Demax, is given as a function of the
    hillslope diffustivity, D, the maximum slope, Smax, and the critical slope
    Sc. 
    
        Demax = D ( 1 + (Smax / Sc)**2 )
    
    The maximum stable time step is given by
    
        dtmax = courant_factor * dx * dx / Demax
    
    Where the courant factor is a user defined scale (default is 0.2)
    
    The CubicNonLinearDiffuser has a boolean flag that permits a user to be 
    warned if timesteps are too large for the slopes in the model grid
    (if_unstable = 'warn') and a boolean flag that turns on dynamic 
    timesteppping (dynamic_dt = False). 
    
    >>> cubicflux.soilflux(2., if_unstable='warn')
    Topographic slopes are high enough such that the Courant condition is 
    exceeded AND you have not selected dynamic timestepping with 
    dynamic_dt=True. This may lead to infinite and/or nan values for slope, 
    elevation, and soil depth. Consider using a smaller time step or dynamic 
    timestepping. The Courant condition recommends a timestep of  0.2 or 
    smaller.
    
    Alternatively you can specify if_unstable='raise', and a Runtime Error will 
    be raised if this condition is not met. 

    Next, lets do an example with dynamic timestepping.
    
    >>> mg = RasterModelGrid((5, 5))
    >>> z = mg.add_zeros('node', 'topographic__elevation')
        
    We'll use a steep slope.
    
    >>> z += mg.node_x.copy()**2
    >>> cubicflux = CubicNonLinearDiffuser(mg)
    
    Lets try to move the soil with a large timestep. Without dynamic time
    steps, this gives a warning that we've exceeded the dynamic timestep size 
    and should use a smaller timestep. We could either use the smaller timestep,
    or specify that we want to use adynamic timestep. 
    
    >>> cubicflux.soilflux(10, if_unstable='warn', dynamic_dt=False)
    Topographic slopes are high enough such that the Courant condition is 
    exceeded AND you have not selected dynamic timestepping with 
    dynamic_dt=True. This may lead to infinite and/or nan values for slope, 
    elevation, and soil depth. Consider using a smaller time step or dynamic 
    timestepping. The Courant condition recommends a timestep of 
    0.004 or smaller.
    
    Now, we'll re-build the grid and do the same exapmle with dynamic timesteps. 
    
    >>> mg = RasterModelGrid((5, 5))
    >>> z = mg.add_zeros('node', 'topographic__elevation')
    >>> z += mg.node_x.copy()**2
    >>> cubicflux = CubicNonLinearDiffuser(mg)
    >>> cubicflux.soilflux(10, if_unstable='warn', dynamic_dt=True)
    >>> np.any(np.isnan(z))
    False
    """

    _name = 'CubicNonLinearDiffuser'

    _input_var_names = set((
        'topographic__elevation',
    ))

    _output_var_names = set((
        'soil__flux',
        'topographic__slope',
        'topographic__elevation',
    ))

    _var_units = {
        'topographic__elevation' : 'm',
        'topographic__slope' : 'm/m',
        'soil__flux' : 'm^2/yr',
    }

    _var_mapping = {
        'topographic__elevation' : 'node',
        'topographic__slope' : 'link',
        'soil__flux' : 'link',
    }

    _var_doc = {
        'topographic__elevation':
                'elevation of the ground surface',
        'topographic__slope':
                'gradient of the ground surface',
        'soil__flux':
                'flux of soil in direction of link', 
    }

    def __init__(self, grid, linear_diffusivity=1., slope_crit=1.,
                 **kwds):
        
        """Initialize CubicNonLinearDiffuser.
        """

        # Store grid and parameters
        self._grid = grid
        self.K = linear_diffusivity
        self.slope_crit = slope_crit

        # Create fields:
        #
        # elevation
        if 'topographic__elevation' in self.grid.at_node:
            self.elev = self.grid.at_node['topographic__elevation']
        else:
            self.elev = self.grid.add_zeros('node', 'topographic__elevation')

        # slope gradient
        if 'topographic__slope' in self.grid.at_link:
            self.slope = self.grid.at_link['topographic__slope']
        else:
            self.slope = self.grid.add_zeros('link', 'topographic__slope')

        # soil flux
        if 'soil__flux' in self.grid.at_link:
            self.flux = self.grid.at_link['soil__flux']
        else:
            self.flux = self.grid.add_zeros('link', 'soil__flux')


    def soilflux(self, dt, dynamic_dt=False, if_unstable='pass', courant_factor=0.2):
        """Calculate soil flux for a time period 'dt'.
        
        Parameters
        ----------

        dt: float (time)
            The imposed timestep.
        dynamic_dt : boolean (optional, default is False)
            Keyword argument to turn on or off dynamic time-stepping
        if_unstable : string (optional, default is "pass")
            Keyword argument to determine how potential instability due to 
            slopes that are too high is handled. Options are "pass", "warn", 
            and "raise". 
        courant_factor : float (optional, default = 0.2)
            Factor to identify stable time-step duration when using dynamic
            timestepping. 
        """
        # establish time left as all of dt
        time_left = dt
        
        # begin while loop for time left
        while time_left > 0.0:

            # Calculate gradients
            self.slope[:] = self.grid.calc_grad_at_link(self.elev)
            self.slope[self.grid.status_at_link == INACTIVE_LINK] = 0.
    
    
            # Test for time stepping courant condition
            De_max = self.K * (1.0 + (self.slope.max()/self.slope_crit)**2.0)
             
            self.dt_max = courant_factor * (self.grid.dx**2) / De_max
    
            # Test for the Courant condition and print warning if user intended
            # for it to be printed. 
            if (self.dt_max < dt) and (dynamic_dt == False) and (if_unstable != 'pass'):
                message = ('Topographic slopes are high enough such that the '
                           'Courant condition is exceeded AND you have not '
                           'selected dynamic timestepping with dynamic_dt=True. '
                           'This may lead to infinite and/or nan values for '
                           'slope, elevation, and soil depth. Consider using a '
                           'smaller time step or dynamic timestepping. The '
                           'Courant condition recommends a timestep of '
                           ''+str(self.dt_max)+' or smaller.')
                if if_unstable == 'raise':
                    raise RuntimeError(message)
                if if_unstable == 'warn':
                    warnings.showwarning(message=message, 
                                         category=RuntimeWarning,
                                         filename=os.path.dirname(os.path.realpath(__file__)),
                                         lineno=219)
                    print(message)

            # if dynamic dt is selected, use it, otherwise, use the entire time
            if dynamic_dt:
                self.sub_dt = np.min([dt, self.dt_max])
                time_left -= self.sub_dt
            else:
                self.sub_dt = dt
                time_left = 0

            # Calculate flux
            self.flux[:] = -(self.K * self.slope
                             + ((self.K/(self.slope_crit**2))
                                * np.power(self.slope, 3)))
    
            # Calculate flux divergence
            dqdx = self.grid.calc_flux_div_at_node(self.flux)
            dqdx[self.grid.status_at_node == CLOSED_BOUNDARY] = 0.
            
            # Update topography
            self.elev -= dqdx * self.sub_dt


    def run_one_step(self, dt, **kwds):
        """
        Advance cubic soil flux component by one time step of size dt.

        Parameters
        ----------
        dt: float (time)
            The imposed timestep.
        """
        self.soilflux(dt, **kwds)    
