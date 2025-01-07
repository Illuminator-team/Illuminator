from illuminator.builder import IlluminatorModel, ModelConstructor

class H2Storage(ModelConstructor):

# TODO Chack what the 'max_h2' and 'min_h2' parameters mean
    parameters={'h2_soc_min': 0,            # Minimum state of charge of the hydrogen storage before discharging stops [%]
                'h2_soc_max': 100,          # Maximum state of charge of the hydrogen storage before charging stops [%]
                'h2_charge_eff': 100,       # Charge efficiency of the H2 storage [%]
                'h2_discharge_eff': 100,    # Discharge efficiency of the H2 storage [%]
                'max_h2': 10,              # maximal flow (?) [kg/timestep]
                'min_h2': -10,              # minimal flow (?) [kg/timestep]
                'h2_capacity_tot':100          # total capacity of the hydrogen stroage [kg]
                }
    
    inputs={'flow2h2storage': 0             # pos or neg flow to H2 storage [kg/timestep]
            
            }
    
    outputs={'h2_in': 0,        # flow into the H2 storage [kg/timestep]
             'h2_out': 0,       # flow out of the H2 storage [kg/timestep]
             'soc': 0,          # state of charge after operation in a timestep [%]
             'mod': 0,          # operating mode (1=charge, -1=discharge, 0=no action) [-]
             'flag': -1         # flag inidicating storage status (1=fully charged, -1=full discharged, 0=available for control) [-]
             }
    states={
            # 'soc': 0,
            # 'flag': 0
            } 
    
    # define other attributes
    time_step_size = 1
    time = None
    
    def step(self, time, inputs, max_advance=1) -> None:

        print("\nH2 storage:")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        # get input data 
        input_data = self.unpack_inputs(inputs)
        print("input data: ", input_data)

        current_time = time * self.time_resolution
        print('from H2 storage %%%%%%%%%%%', current_time)

        print('state of charge h2 storage: ', self._model.outputs['soc'])
        print('New state of charge: ', self.soc)
        print("outputs:", self.outputs)
        
        return time + self._model.time_step_size
    
    def discharge(self, flow2h2storage):

        flow = max(self.min_h2, flow2h2storage) # discharged h2 must be minimally the min_h2
        h22discharge = flow2h2storage * self.time_resolution / self.h2_discharge_eff # the amoount of hydrogen desired to be discharged (neg)
        h2_capacity = (self.soc_min - self.soc) / 100 * self.h2_capacity_tot # amount of h2 that can be discharged (neg)
        if self.soc <= self.soc_min:
            self.flag = -1
            self.h2_out = 0
        else:
            if h22discharge > h2_capacity: # both negative for the code so the sign is inverted
                # there is enough h2 in the storage to discharge the desired h2
                self.soc += h22discharge / self.h2_capacity_tot * 100
                self.flag = 0       #
                self.h2_out = flow
            else: 
                # only the available amount can be discharged
                self.soc = self.soc_min
                self.flag = -1 # fully discharged
                self.h2_out = h2_capacity / self.h2_discharge_eff / self.time_resolution
        self.soc = round(self.soc, 3)
        re_params = {'h2_in': flow,        
             'h2_out': self.h2_out,       
             'soc': self.soc,          
             'mod': -1,          
             'flag': self.flag
             }
        return re_params
    
    def charge(self, flow2h2storage):
        
        flow = min(self.max_h2, flow2h2storage)
        h22charge = flow2h2storage * self.time_resolution * self.h2_charge_eff # the amoount of hydrogen desired to be charged (pos)
        h2_capacity = (self.soc_max - self.soc) / 100 * self.h2_capacity_tot # amount of h2 that can be charged till full (pos)
        if self.soc >= self.soc_max:
            self.flag = 1
            self.h2_out = 0
        else:
            if h22charge <= h2_capacity:
                # enough storage capacity left to charge the desired amount of h2
                self.soc += h22charge / self.h2_capacity_tot * 100
                self.h2_out = h22charge
                self.flag = 0
            else:
                # only the available capacity can be filled with h2
                self.soc = self.h2_soc_max
                self.flag = 1
                self.h2_out = h2_capacity / self.h2_charge_eff / self.time_resolution
        self.soc = round(self.soc, 3)
        re_params = {'h2_in': flow,        
             'h2_out': self.h2_out,       
             'soc': self.soc,          
             'mod': 1,          
             'flag': self.flag
             }
        return re_params


    def output_flow(self, flow2h2storage, soc):
        self.soc = soc
        if flow2h2storage == 0:         # no action
            # Here the state of the storage is updated in case there is no supply/demand
            if soc >= self.soc_max:     # storage is fully charged
                self.flag = 1
            elif soc <= self.soc_min:   # storage fully discharged
                self.flag = -1
            else:
                self.flag = 0           # storage available to operate
            # TODO: add the re_params output
        elif flow2h2storage < 0:        # in case of demand
            re_params = self.discharge(flow2h2storage) # storage is discharged
        else:                           # in case of supply
            re_params = self.charge(flow2h2storage) # storage is charged
        return re_params