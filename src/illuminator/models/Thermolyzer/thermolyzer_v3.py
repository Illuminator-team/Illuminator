from illuminator.builder import ModelConstructor

class Thermolyzer(ModelConstructor):
    parameters={
            'eff' : 70,             # thermolyzer effficiency [%]  
            'C_bio_h2' : 60,        # conversion factor from biomass to hydrogen [-] 
            'C_CO2' : 10,           # absorption factor carbondioxide per h2 produced [-] 
            'C_Eelec_h2': 11.5,     # conversion factor electrical energy to hydrogen mass [kWh/kg]    
            'max_ramp_up' : 10      # maximum ramp up in power per timestep [kW/timestep]  
            
    },
    inputs={
            'biomass_in' : 0,       # biomass input [kg/timestep]
            'flow2t' : 0            # power input to the thermolyzer [kW]
            # 'water_in' : 0        # water input to the thermolzyer [L/timestep]

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

        h_flow = self.generate(
            m_bio=input_data['biomass_in'],
            flow2t=input_data['flow2t'],
            max_advance = max_advance
            )
        h_gen = h_flow * self.time_resolution
        CO2_out = -h_gen * input_data['C_CO2']
        self._model.outputs['h_gen'] = h_gen
        self._model.outputs['CO2_out'] = CO2_out
        print("outputs:", self.outputs)
        
        return time + self._model.time_step_size
    
    def ramp_lim(self, flow2t, max_advance):
        """
        Limits the thermolizer input flow

        ...

        Parameters
        ----------
        flow2t : float
            output pressure [kg/timestep]

        Returns
        -------
        density : float
            The new found density after compression [kg/m3]
        """
        # restrict the power input to not increase more than max_p_ramp_rate
        # compared to the last timestep
        # TODO: check method of using paramters (self. or .get())
        p_change = flow2t - self.p_in_last
        if abs(p_change) > self.max_p_ramp_rate:
            if p_change > 0:
                power_in = self.p_in_last + self.max_p_ramp_rate * max_advance
            else:
                power_in = self.p_in_last - self.max_p_ramp_rate * max_advance
        else:
            power_in = flow2t
        self.p_in_last = power_in
        return power_in
        

    def generate(self, m_bio, flow2t, max_advance = 1):
        # TODO: add water dependency once the conversion factor is known
        # restrict the input power to be maximally max_p_in
        power_in = min(flow2t, self.max_p_in) 
        # restrict input power with ramp limits
        power_in = self.ramp_lim(flow2t, max_advance)
        # the production of hyrdogen is dependent on both the available biomass mass and the input power. Therfor:
        # calculate potential generation of h2 for both dependencies
        h_prod_p = power_in / self.C_Eelec_h2 / 3600    # [kg/s] (/3600 comes from kWh to kWs)
        h_prod_m = m_bio / self.C_bio_h2                # [kg/s]
        h_out = min(h_prod_p, h_prod_m)
        return h_out