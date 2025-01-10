from illuminator.builder import IlluminatorModel, ModelConstructor
from numpy import log, pi

# construct the model
class Wind(ModelConstructor):

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

    # define step function
    def step(self, time, inputs, max_advance=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        

        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time
        eid = list(self.model_entities)[0]  # there is only one entity per simulator, so get the first entity
        current_time = time * self.time_resolution
        print('from wind %%%%%%%%%%%', current_time)

        self.resolution_h = self.time_resolution/60/60  # convert scenario resolution to hours
        results = self.generation(u=input_data['u'])

        print(f"u: {input_data['u']}, output: {results['wind_gen']}")

        self.set_outputs(results)
        self.set_states({'u60': self.u60})

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


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
        radius = self.diameter/2
        air_density = 1.225

        self.u60 = u*((60/100)**0.14)
        self.u25 = self.u60 * (log(20 / 0.2) / log(60 / 0.2))

        if self.output_type == 'energy':
            p = ((0.5 * (self.u25 ** 3) * (pi * (radius ** 2.0)) * air_density * self.cp)/1000) * self.resolution_h  # kWh
        elif self.output_type == 'power':
            p = ((0.5 * (self.u25 ** 3) * (pi * (radius ** 2.0)) * air_density * self.cp) / 1000)  # kW
        re_params = {'wind_gen': p, 'u': self.u25}
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
        self.u60 = u * ((60 / 100) ** 0.14)
        self.u25 = self.u60 * (log(20 / 0.2) / log(60 / 0.2))

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

