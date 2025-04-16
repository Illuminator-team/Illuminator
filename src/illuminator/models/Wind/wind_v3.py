from numpy import log, pi
from illuminator.builder import ModelConstructor

# construct the model
class Wind(ModelConstructor):
    """
    A wind turbine model that calculates power generation based on wind speed.
    
    This model simulates wind turbine performance considering wind speed at different
    heights, power curve characteristics, and system parameters. It can output
    either power or energy values.

    Parameters
    ----------
    p_rated : float
        Rated power output (kW) at rated wind speed
    u_rated : float
        Rated wind speed (m/s)
    u_cutin : float
        Cut-in wind speed (m/s)
    u_cutout : float
        Cut-out wind speed (m/s)
    cp : float
        Coefficient of performance (Betz limit max 0.59)
    diameter : float
        Rotor diameter (m)
    output_type : str
        Output type ('power' or 'energy')
    
    Inputs
    ----------
    u : float
        Wind speed at hub height (m/s)

    Outputs
    ----------
    wind_gen : float
        Wind generation in kW or kWh
    u : float
        Adjusted wind speed at 25m height (m/s)
    
    States
    ----------
    u60 : float
        Wind speed at 60m height (m/s)
    u25 : float
        Wind speed at 25m height (m/s)
    """
    # Define the model parameters, inputs, outputs...
    # all parameters will be directly available as attributes
    parameters={'p_rated': 500,  # Rated power output (kW) of the wind turbine at the rated wind speed and above.
                'u_rated': 100,  # Rated wind speed (m/s) where the wind turbine reaches its maximum power output.
                'u_cutin': 1,  # Cut-in wind speed (m/s) below which the wind turbine does not generate power.
                'u_cutout': 1000,  # Cut-out wind speed (m/s) above which the wind turbine stops generating power to prevent damage.
                'cp': 0.40,  # Coefficient of performance of the wind turbine, typically around 0.40 and never more than 0.59.
                'diameter': 30,  # Diameter of the wind turbine rotor (m), used in calculating the swept area for wind power production.
                'output_type': 'power'  # Output type of the wind generation, either 'power' (kW) or 'energy' (kWh).
                }
    inputs={'u': 0,  # Wind speed (m/s) at a specific height used to calculate the wind power generation.
            }
    outputs={'wind_gen': 0,  # Generated wind power output (kW) or energy (kWh) based on the chosen output type (power or energy).
             'u': 0  # Adjusted wind speed (m/s) at 25m height after converting from the original height (e.g., 100m or 60m).
             }
    states={'u60': 10,  # Wind speeds adjusted for 60m height using logarithmic wind profile equations.
            'u25': 0  # Wind speeds adjusted for 25m height using logarithmic wind profile equations.
            }

    # define other attributes
    time_step_size=1
    time=None
    powerout = 0  # Output power of the wind turbine at a specific wind speed u.
    u60 = 10  # Wind speeds adjusted for different heights (e.g., 60m and 25m) using logarithmic wind profile equations.
    u25 = 0  # Wind speeds adjusted for different heights (e.g., 60m and 25m) using logarithmic wind profile equations.


    def __init__(self, **kwargs) -> None:
        """
        Initialize the Wind model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the wind turbine model,
            including rated power, cut-in/out speeds, rotor diameter, and
            performance coefficient.
        """
        super().__init__(**kwargs)
        self.u_rated = self.parameters['u_rated']
        self.u_cutin = self.parameters['u_cutin']
        self.u_cutout = self.parameters['u_cutout']
        self.p_rated = self.parameters['p_rated']
        self.cp = self.parameters['cp']
        self.diameter = self.parameters['diameter']
        self.output_type = self.parameters['output_type']



    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time in seconds
            inputs (dict): Dictionary containing input values:
            - u (float): Wind speed [m/s] at hub height
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 1.
        Returns:
            float: Next simulation time in seconds
        """
        self.resolution_h = self.time_resolution / 60 / 60  # convert scenario resolution to hours
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible

        results = self.generation(u=input_data['u'])

        self.set_outputs(results)
        self.set_states({'u60': self.u60})

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def production(self, u:float) -> dict:
        """
        Calculates the wind power production using the basic wind power equation.

        The function accounts for air density, rotor area, and the wind turbine's
        coefficient of performance. It also adjusts wind speeds for different heights
        using logarithmic wind profile equations.

        Parameters
        ----------
        u : float
            Wind speed at hub height (100m) in m/s

        Returns
        -------
        dict
            Dictionary containing:
            - wind_gen: Power output in kW or energy output in kWh
            - u: Adjusted wind speed at 25m height in m/s
        """
        radius = self.diameter/2
        air_density = 1.225

        self.u60 = u*((60/100)**0.14)
        self.u25 = self.u60 * (log(20 / 0.2) / log(60 / 0.2))

        p = 0
        if self.output_type == 'energy':
            p = ((0.5 * (self.u25 ** 3) * (pi * (radius ** 2.0)) * air_density * self.cp)/1000) * self.resolution_h  # kWh
        elif self.output_type == 'power':
            p = ((0.5 * (self.u25 ** 3) * (pi * (radius ** 2.0)) * air_density * self.cp) / 1000)  # kW
        else:
            raise ValueError(f"Invalid output_type: {self.output_type}. Must be 'power' or 'energy'")

        re_params = {'wind_gen': p, 'u': self.u25}
        return re_params

    def generation(self, u:float) -> dict:
        """
        Calculates the final wind power output considering cut-in/out speeds and rated power.

        This function determines the actual power output based on the adjusted wind speed,
        taking into account the turbine's operational limits such as cut-in speed,
        rated speed, and cut-out speed.

        Parameters
        ----------
        u : float
            Wind speed at hub height (100m) in m/s

        Returns
        -------
        dict
            Dictionary containing:
            - wind_gen: Power output in kW or energy output in kWh
            - u: Adjusted wind speed at 25m height in m/s
        """
        self.u60 = u * ((60 / 100) ** 0.14)
        self.u25 = self.u60 * (log(20 / 0.2) / log(60 / 0.2))

        re_params = {}
        if self.u25 >= self.u_rated:
            if self.u25 == self.u_rated:
                if self.output_type == 'power':
                    re_params = {'wind_gen': (self.p_rated), 'u': self.u25}
                elif self.output_type == 'energy':
                    re_params = {'wind_gen': (self.p_rated * self.resolution_h), 'u': self.u25}
            elif self.u25 <= self.u_cutout:
                if self.output_type == 'power':
                    re_params = {'wind_gen': (self.p_rated), 'u': self.u25}
                elif self.output_type == 'energy':
                    re_params = {'wind_gen': (self.p_rated * self.resolution_h), 'u': self.u25}
            else:
                re_params = {'wind_gen': 0, 'u': self.u25}
                # return re_params
        elif self.u25 < self.u_cutin:
            re_params = {'wind_gen': 0, 'u': self.u25}
        else:
            re_params = self.production(u)
        return re_params

