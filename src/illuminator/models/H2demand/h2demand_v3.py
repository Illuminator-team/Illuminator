from illuminator.builder import ModelConstructor

# construct the model
class H2demand(ModelConstructor):
    """
    A class to represent an H2demand model.
    This class provides methods to simulate the demand of hydrogen gas.

    Attributes
    ----------
    parameters : dict
        Dictionary containing model parameters such as the number of demand units.
    inputs : dict
        Dictionary containing input variables like the demand of hydrogen mass per timestep.
    outputs : dict
        Dictionary containing calculated outputs like the total consumption for each timestep.
    states : dict
        Dictionary containing the state variables of the demand model.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    -------
    step(time, inputs, max_advance=1)
        Simulates one time step of the demand model.
    demand(demand, units)
        Calculates the total demand given the amount of equally sized units.
    """
    parameters={'units': 1          # number of demand units
                }
    inputs={'demand': 0}            # demand of hydrogen mass per timestep [kg/timestep]
    outputs={'tot_dem': 0           # total consumption for each timetep (= demand input for units = 1) [kg/timestep]
             }
    states={
            # 'consumption': 0,
            # 'time': None
            }
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the H2demand model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.units = self._model.parameters.get('units')
        self.time_step_size = self._model.parameters.get('time_step_size')
        self.time = self._model.parameters.get('time')

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> int:
        """
        Simulates one time step of the H2demand model.

        This method processes the inputs for one timestep, updates the demand state based on
        the hydrogen demand, and sets the model outputs accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - demand: Hydrogen demand in kg/timestep
        max_advance : int, optional
            Maximum time step size (default 1)

        Returns
        -------
        int
            Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)
        self.time = time

        current_time = time * self.time_resolution
        print('from h2demand %%%%%%%%%%%', current_time)   

        
        self._model.outputs['p_out'] = self.demand(input_data['demand'], self.units)
        print("outputs:", self.outputs)

        return time + self._model.time_step_size
    


    def demand(self, demand:float, units:int) -> float:
        """
        Calculates the total demand given the amount of equally sized units

        ...

        Parameters
        ----------
        demand : float
            demand of h2 for each timestep [kg/timestep]

        units : int
            amount of equally sized units od demand

        Returns
        -------
        tot_dem : float
            Total demand of h2 [kg/timestep]
        """
        dem_tot = demand * units    # [kg/timestep]

        return dem_tot

# if __name__ == '__main__':
#     # Create a model by inheriting from ModelConstructor
#     # and implementing the step method
#     load_model = H2demand(h2demand)