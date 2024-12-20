from illuminator.builder import IlluminatorModel, ModelConstructor

class Thermolyzer(ModelConstructor):
    parameters={
            'eff' : 70,             # thermolyzer effficiency [%]  
            'C_bio_h2' : 60,        # conversion factor from biomass to hydrogen [-] 
            'C_bio_CO2' : 40,       # conversion factor from biomass to carbondioxide [-] 
            'max_ramp_up' : 10      # maximum ramp up in power per timestep [kW/timestep]  
            
    },
    inputs={
            'biomass_in' : 0,       # biomass input [kg/timestep]
            'power_in' : 0,         # power input to the thermolyzer [kW]
            'water_in' : 0          # water input to the thermolzyer [L/timestep]

    },
    outputs={
            'h_gen' : 0,            # hydrogen generation [kg/timestep]
            'CO2_out' : 0           # CO2 output [kg/timestep]

    },
    states={},


    # other attributes
    time_step_size=1,
    time=None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
    



    def step(self, time, inputs, max_advance=1) -> None:

        print("\nThermolyzer:")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        # get input data 
        input_data = self.unpack_inputs(inputs)
        print("input data: ", input_data)

        current_time = time * self.time_resolution
        print('from electrolyzer %%%%%%%%%%%', current_time)

        # h_gen = h_flow * self.time_resolution          
        # self._model.outputs['h_gen'] = h_gen
        print("outputs:", self.outputs)
        
        return time + self._model.time_step_size
    
    def ramp_lim(self, flow2e, max_advance):
        # restrict the power input to not increase more than max_p_ramp_rate
        # compared to the last timestep
        # TODO: check method of using paramters (self. or .get())
        p_change = flow2e - self.p_in_last
        if abs(p_change) > self.max_p_ramp_rate:
            if p_change > 0:
                power_in = self.p_in_last + self.max_p_ramp_rate * max_advance
            else:
                power_in = self.p_in_last - self.max_p_ramp_rate * max_advance
        else:
            power_in = flow2e
        self.p_in_last = power_in
        return power_in
        

    def generate(self, flow2e, eff, hhv, mmh2, max_advance):
        # restrict the input power to be maximally max_p_in
        flow2e = min(flow2e, self.max_p_in) 
        power_in = self.ramp_lim(flow2e, max_advance)
        h_out = (power_in * eff * mmh2) / (hhv * 1000)
        return h_out