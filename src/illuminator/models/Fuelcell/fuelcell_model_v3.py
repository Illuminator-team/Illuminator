from illuminator.builder import IlluminatorModel, ModelConstructor

class Fuelcell(ModelConstructor):
    parameters={
            'fuelcell_eff': 99,     # fuelcell efficiency [%]
            'h2_max' : 10,          # max hyrogen input flow [kg/timestep]  
            'h2_min' : 0            # min hydrogen input flow [kg/timestep]
    },
    inputs={
            'h2_flow2f' : 0         # hydrogen flow to the fuelcell [kg/timestep]
    },
    outputs={
            'p_out' : 0             # power output [kW]
    },
    states={},


    # other attributes
    time_step_size=1,
    time=None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [g/mol]
 
    def step(self, time, inputs, max_advance=1) -> None:

        print("\nFuelcell:")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        # get input data 
        input_data = self.unpack_inputs(inputs)
        print("input data: ", input_data)

        current_time = time * self.time_resolution
        print('from fuelcell %%%%%%%%%%%', current_time)



        self._model.outputs['p_out'] = self.power_out(input_data['h2_flow2f'])
        print("outputs:", self.outputs)
        return time + self._model.time_step_size
    

def power_out(self, h2_flow2f):
    """
    Calculates the output power of the fuelcell

    ...

    Parameters
    ----------
    h2_flow2f : float
        H2 flow into the fuelcell [kg/timestep]

    Returns
    -------
    p_out : float
        The outout power of the fuelcell [kW]
    """
    # limit hydrogen consumption by the minimum and maximum hydrogen the fuelcell can accept
    h2_flow = max(self.h2_min, min(self.h2_max, h2_flow2f))         # [kg/timestep]
    h2_flow = h2_flow / self.timestep                               # [kg/s]
    p_out = (h2_flow * self.fuelcell_eff * self.hhv) / self.mmh2    # [kW]
    return p_out

# TODO: Ramping limits implementation