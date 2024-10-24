import numpy as np
from numpy import genfromtxt
import math


# this model will be called by the step method in the wind_SimAPI file and there it will get input for calculations.
# remove the input of turbine height and just make changing the wind speed to a height of 80m by default.

class wind_py_model:

    def __init__(self, p_rated, u_rated, u_cutin, u_cutout, diameter, cp, output_type:str='power',resolution:float=15) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the wind_mosaik.WindSim class.

        ...

        Parameters
        ----------
        p_rated : ???
            kW power it generates at rated wind speed and above
        u_rated : ???
            m/s windspeed it generates most power at
        u_cutin : ???
            m/s below this wind speed no power generation
        u_cutout : ???
            m/s above this wind speed no power generation. Blades are pitched
        diameter  : ???
            ???
        cp : ???
            Coefficient of performance of a turbine. Usually around0.40. Never more than 0.59
        output_type : str
            'power' or 'energy'
        resolution : float
            ???

        Attributes
        ----------
        self.p_rated : ???
            kW power it generates at rated wind speed and above
        self.u_rated : ???
            m/s windspeed it generates most power at
        self.u_cutin : ???
            m/s below this wind speed no power generation
        self.u_cutout : ???
            m/s above this wind speed no power generation. Blades are pitched
        self.cp : ???
            Coefficient of performance of a turbine. Usually around0.40. Never more than 0.59
        self.powerout : float
            Output power at wind speed u
        self.dia : ???
            ???
        self.output_type : str
            'power' or 'energy'
        self.resolution : float
            ???
        self.time_interval : float
            hours (15 minutes time interval/ number of minutes in an hour)
        """
        self.p_rated = p_rated  # kW power it generates at rated wind speed and above
        self.u_rated = u_rated  # m/s #windspeed it generates most power at
        self.u_cutin = u_cutin  # m/s #below this wind speed no power generation
        self.u_cutout = u_cutout  # m/s #above this wind speed no power generation. Blades are pitched
        self.cp = cp  # coefficient of performance of a turbine. Usually around0.40. Never more than 0.59
        self.powerout = 0  # output power at wind speed u
        self.dia = diameter
        self.output_type = output_type  # 'power' or 'energy'
        self.resolution = resolution
        self.time_interval = self.resolution / 60  # hours (15 minutes time interval/ number of minites in an hour)

    def production(self, u:float) -> dict:
        """
        Calculates the production (?)

        ...

        Parameters
        ----------
        u : float
            ???

        Returns
        -------
        new_step : int
            Return the new simulation time, i.e. the time at which ``step()`` should be called again.
        """
        radius = self.dia/2
        air_density = 1.225
        self.resolution = 15
        self.time_interval = self.resolution/60  #hours (15 minutes time interval/ number of minites in an hour)

        u60 = u*((60/100)**0.14)
        u25 = u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if self.output_type == 'energy':
            p = ((0.5 * (u25 ** 3) * (math.pi * (radius ** 2.0)) * air_density * self.cp)/1000) * self.time_interval  # kWh
        elif self.output_type == 'power':
            p = ((0.5 * (u25 ** 3) * (math.pi * (radius ** 2.0)) * air_density * self.cp) / 1000)  # kW
        re_params = {'wind_gen': p, 'u': u25}
        return re_params

    def generation(self, u:float) -> dict:
        """
        Calculates the generation (?)

        ...

        Parameters
        ----------
        u : float
            ???

        Returns
        -------
        new_step : int
            Return the new simulation time, i.e. the time at which ``step()`` should be called again.
        """
        u60 = u * ((60 / 100) ** 0.14)
        u25 = u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if u25 >= self.u_rated:
            if u25 == self.u_rated:
                if self.output_type == 'power':
                    re_params = {'wind_gen': (self.p_rated), 'u': u25}
                elif self.output_type == 'energy':
                    re_params = {'wind_gen': (self.p_rated * self.time_interval), 'u': u25}
            elif u25 <= self.u_cutout:
                if self.output_type == 'power':
                    re_params = {'wind_gen': (self.p_rated), 'u': u25}
                elif self.output_type == 'energy':
                    re_params = {'wind_gen': (self.p_rated * self.time_interval), 'u': u25}
            else:
                re_params = {'wind_gen': 0, 'u': u25}
                # return re_params
        elif u25 < self.u_cutin:
            re_params = {'wind_gen': 0, 'u': u25}
        else:
            re_params = self.production(u)
        return re_params

