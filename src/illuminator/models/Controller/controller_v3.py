from illuminator.builder import IlluminatorModel, ModelConstructor

# construct the model
class Controller(ModelConstructor):

    parameters={'soc_min': 0,  # Minimum state of charge of the battery before discharging stops
                'soc_max': 100,  # Maximum state of charge of the battery before charging stops
                'h2_soc_min': 0,  # Minimum state of charge of the hydrogen storage before discharging stops
                'h2_soc_max': 100,  # Maximum state of charge of the hydrogen storage before charging stops
                'fc_eff': 100  # Efficiency of the fuel cell
                }
    inputs={'wind_gen': 0,  # Wind power generation
            'pv_gen': 0,  # Solar power generation
            'load_dem': 0,  # Electrical load demand
            'soc': 0,  # State of charge of the battery
            'h2_soc': 0  # State of charge of the hydrogen storage
            }
    outputs={'flow2b': 0,  # Power flow to/from battery (positive for charging, negative for discharging)
             'flow2e': 0,  # Power flow to the electrolyzer for hydrogen production
             'dump': 0,  # Excess power that cannot be stored or used
             'h2_out': 0  # Hydrogen output from fuel cell to meet demand (positive if used, zero otherwise)
             }
    states={}
    
    # define other attributes
    time_step_size = 1
    time = None
    flow_b = 0  # Internal state representing the power flow to/from battery
    flow_e = 0  # internal state representing the power flow to the electrolyzer
    dump = 0  # Internal state representing excess power
    h_out = 0  # Internal state representing the hydrogen output from the fuel cell to meet the demand

    # define step function
    def step(self, time, inputs, max_advance=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.

        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time
        eid = list(self.model_entities)[0]  # there is only one entity per simulator, so get the first entity

        current_time = time * self.time_resolution
        print('from controller %%%%%%%%%%%', current_time)

        results = self.control(
            wind_gen=input_data['wind_gen'],
            pv_gen=input_data['pv_gen'],
            load_dem=input_data['load_dem'],
            soc=input_data['soc'],
            h2_soc=input_data['h2_soc']
            )

        
        self._model.outputs['flow2b'] = results['flow2b']
        self._model.outputs['flow2e'] = results['flow2e']
        self._model.outputs['dump'] = results['dump']
        self._model.outputs['h2_out'] = results['h2_out']


        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def control(self, wind_gen:float, pv_gen:float, load_dem:float, soc:int, h2_soc:int) -> dict:
        """
        Checks the state of flow based on wind and solar energy generation compared to demand.

        ...

        Parameters
        ----------
        wind_gen : float
            ???
        pv_gen : float 
            ???
        load_dem : float
            ???
        soc : int
            Value representing the state of charge (SOC)
        h2_soc : int
            ???
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        self.soc_b = soc
        self.soc_h = h2_soc
        flow = wind_gen + pv_gen - load_dem  # kW

        if flow < 0:  # means that the demand is not completely met and we need support from battery and fuel cell
            if self.soc_b > self.soc_min:  # checking if soc is above minimum. It can be == to soc_max as well.
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0

            elif self.soc_b <= self.soc_min:
                self.flow_b = 0
                q = 39.4
                self.h_out = (flow / q) / self.fc_eff

                print('Battery Discharged')


        elif flow > 0:  # means we have over generation and we want to utilize it for charging battery and storing hydrogen
            if self.soc_b < self.soc_max:
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0
            elif self.soc_b == self.soc_max:
                self.flow_b = 0
                if self.soc_h < self.h2_soc_max:
                    self.flow_e = flow
                    self.dump = 0
                    self.h_out = 0
                elif self.soc_h == self.h2_soc_max:
                    self.flow_e = 0
                    self.dump = flow
                    self.h_out = 0

        re_params = {'flow2b': self.flow_b, 'flow2e': self.flow_e, 'dump': self.dump, 'h2_out':self.h_out}
        return re_params