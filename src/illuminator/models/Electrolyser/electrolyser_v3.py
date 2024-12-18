from illuminator.builder import IlluminatorModel, ModelConstructor

class Electrolyzer(ModelConstructor):
    parameters={
            'e_eff' : 70,       # electrolyzer effficiency [%]
            'max_p_in' : 10,    # maximum input power [kW]
            'max_p_ramp_rate' : 10   # maximum rampup power [kW/timestep]
            
    },
    inputs={
            'flow2e' : 0        # power flow to the electrolyzer [kW]

    },
    outputs={
            'h_gen' : 0         # hydrogen generation [kg/timestep]
            # 'water_used' : 0    # water required for H2 prodcution [kg/timestep]
    },
    states={},


    # other attributes
    time_step_size=1,
    time=None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
    p_in_last = 0               # the initial power is initialised to 0 [kW]



    def step(self, time, inputs, max_advance=1) -> None:

        print("\nElectrolyzer:")
        print("inputs (passed): ")
        print("outputs (passed): ")
        # get input data 
        input_data = self.unpack_inputs(inputs)
        print("input data: ", input)

        current_time = time * self.time_resolution
        print('from coelectrolyzer %%%%%%%%%%%', current_time)

        # calculate generation provided the desired input power  
        h_gen = self.generate(
            flow2e=input(input_data['flow2e']),
            eff=self.e_eff,
            hhv=self.hhv,
            mmh2=self.mmh2,
            max_advance = max_advance
            )           
        self._model.outputs['h_gen'] = h_gen
        return time + self._model.time_step_size
    
    def ramp_lim(self, flow2e, max_advance):
        # restrict the power input to not increase more than max_p_ramp_rate
        # compared to the last timestep
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
        h_out = power_in * eff / hhv * mmh2 / 1000
        return h_out