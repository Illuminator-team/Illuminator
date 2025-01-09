from illuminator.builder import IlluminatorModel, ModelConstructor

# construct the model
class H2demand(ModelConstructor):
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


    def step(self, time, inputs, max_advance=1) -> None:

        input_data = self.unpack_inputs(inputs)
        self.time = time

        current_time = time * self.time_resolution
        print('from h2demand %%%%%%%%%%%', current_time)   

        
        self._model.outputs['p_out'] = self.demand(input_data['demand', self.units])
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

if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    load_model = H2demand(h2demand)