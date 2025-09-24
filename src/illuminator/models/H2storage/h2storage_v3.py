# from illuminator.builder import ModelConstructor

# class H2Storage(ModelConstructor):
    # """
    # A class to represent an H2 Storage model.
    # This class provides methods to simulate the charging and discharging of hydrogen storage.

    # Attributes
    # ----------
    # parameters : dict
    #     Dictionary containing storage parameters such as minimum and maximum state of charge, charge and discharge efficiency, and total capacity.
    # inputs : dict
    #     Dictionary containing input variables like flow to the hydrogen storage.
    # outputs : dict
    #     Dictionary containing calculated outputs like flow into and out of the storage, state of charge, operating mode, and storage status flag.
    # states : dict
    #     Dictionary containing the state variables of the storage model.
    # time_step_size : int
    #     Time step size for the simulation.
    # time : int or None
    #     Current simulation time.

    # Methods
    # -------
    # step(time, inputs, max_advance=1)
    #     Simulates one time step of the hydrogen storage model.
    # discharge(flow2h2storage)
    #     Simulates the discharging process based on the state of charge and the incoming flow.
    # charge(flow2h2storage)
    #     Simulates the charging process based on the state of charge and the incoming flow.
    # output_flow(flow2h2storage, soc)
    #     Controller that determines to charge, discharge, or do nothing based on the desired flow.
    # """

   
    

# # TODO Chack what the 'max_h2' and 'min_h2' parameters mean
#     parameters={'h2_soc_min': 0,            # Minimum state of charge of the hydrogen storage before discharging stops [%]
#                 'h2_soc_max': 100,          # Maximum state of charge of the hydrogen storage before charging stops [%]
#                 'h2_charge_eff': 100,       # Charge efficiency of the H2 storage [%]
#                 'h2_discharge_eff': 100,    # Discharge efficiency of the H2 storage [%]
#                 'max_h2': 10,               # maximal flow (?) [kg/timestep]
#                 'min_h2': 10,              # minimal flow (?) [kg/timestep]
#                 'h2_capacity_tot':100       # total capacity of the hydrogen strorage [kg]
#                 }
    
#     inputs={'h2_gen': 0,             # pos or neg flow to H2 storage [kg/timestep]
#             'h2_out':0               # Hydrogen output from fuel cell to meet demand (positive if used, zero otherwise)
            
#             }
#     outputs={'h2_in': 0,        # flow into the H2 storage [kg/timestep]
#              'h2_flow2f': 0        # flow out of the H2 storage [kg/timestep]

#              }
#     states={
#              'h2_soc': 0,          # state of charge after operation in a timestep [%]
#              'mod': 0,          # operating mode (1=charge, -1=discharge, 0=no action) [-]
#              'flag': 0          # flag inidicating storage status (1=fully charged, -1=full discharged, 0=available for control) [-]
#             }
    
#     # define other attributes
#     time_step_size = 1
#     time = None
    
#     def __init__(self, **kwargs) -> None:
#         """
#         Initialize the H2 Storage model with the provided parameters.

#         Parameters
#         ----------
#         kwargs : dict
#             Additional keyword arguments to initialize the model.
#         """
#         super().__init__(**kwargs)
#         self.h2_soc_min = self._model.parameters.get('h2_soc_min')
#         self.h2_soc_max = self._model.parameters.get('h2_soc_max')
#         self.h2_charge_eff = self._model.parameters.get('h2_charge_eff')/100
#         self.h2_discharge_eff = self._model.parameters.get('h2_discharge_eff')/100
#         self.max_h2 = self._model.parameters.get('max_h2')
#         self.min_h2 = self._model.parameters.get('min_h2')
#         self.h2_capacity_tot = self._model.parameters.get('h2_capacity_tot')
#         self.h2_soc = self._model.states.get('h2_soc')
#         self.flag = self._model.states.get('flag')

#     def step(self, time: int, inputs: dict=None, max_advance: int = 900) -> None:
#         """
#         Simulates one time step of the hydrogen storage model.

#         This method processes the inputs for one timestep, updates the hydrogen storage state based on
#         the hydrogen flow, and sets the model outputs accordingly.

#         Parameters
#         ----------
#         time : int
#             Current simulation time
#         inputs : dict
#             Dictionary containing input values, specifically:
#             - flow2h2storage: Hydrogen flow to the storage in kg/timestep
#         max_advance : int, optional
#             Maximum time step size (default 900)

#         Returns
#         -------
#         int
#             Next simulation time step
#         """
#         input_data = self.unpack_inputs(inputs)

#         current_time = time * self.time_resolution
#         print('from H2 storage %%%%%%%%%%%', current_time)
#         results = self.output_flow(input_data['h2_gen'])
#         results = self.output_flow(input_data['h2_out'])
#         self.set_outputs({'h2_in': results['h2_in'], 'h2_flow2f': results['h2_flow2f']})
#         self.set_states({'h2_soc': results['h2_soc'], 'mod': results['mod'], 'flag': results['flag']})
#         return time + self._model.time_step_size
    
#     def discharge(self, h2_out:float) -> dict:
#         """
#         Simulates the discharging process based on the soc and the incoming flow. Returns parameters based on the capacbilities of the h2 storage

#         ...

#         Parameters
#         ----------
#         flow2h2storage : float
#             Desired output flow (negative) [kg/timestep]

#         Returns
#         -------
#         re_params : dict
#             Collection of parameters and their respective values
#         """
#         flow = max(self.min_h2, h2_out) # discharged h2 must be minimally the min_h2
#         if (flow < 0):
#             h22discharge = flow * self.time_resolution / self.h2_discharge_eff # the amount of hydrogen desired to be discharged (neg)
#             h2_capacity = (self.h2_soc_min - self.h2_soc) / 100 * self.h2_capacity_tot # amount of h2 that can be discharged (neg)
#             if self.h2_soc <= self.h2_soc_min:
#                 self.flag = -1
#                 self.h2_flow2f = 0
#             else: 
#                 if h22discharge > h2_capacity:
#                     self.h2_flow2f = flow
#                     self.h2_soc = self.h2_soc + h22discharge/ self.h2_capacity_tot * 100  # Update SOC
#                     self.flag = 0  # Available for operation
#                 else:
#                     self.h2_flow2f = h2_capacity * self.h2_discharge_eff  # Flow does not meet minimum requirement
#                     self.h2_soc = self.h2_soc_min
#                     self.flag = 0
#         self.h2_soc = round(self.h2_soc, 3)
#         re_params = {'h2_in': flow,        
#                     'h2_flow2f': self.h2_flow2f,       
#                     'h2_soc': self.h2_soc,          
#                     'mod': -1,          
#                     'flag': self.flag}
#         return re_params
    
#     def charge(self, h2_gen):
#         """
#         Simulates the charging process based on the soc and the incoming flow. Returns parameters based on the capacbilities of the h2 storage.

#         ...

#         Parameters
#         ----------
#         flow2h2storage : float
#             Desired output flow (positive) [kg/timestep]

#         Returns
#         -------
#         re_params : dict
#             Collection of parameters and their respective values
#         """
                
#         flow = min(self.max_h2, h2_gen)
#         print(f"DEBUG: This amount of hydrogen arrives at the storage before eff: {flow}")
#         h22charge = flow * self.h2_charge_eff # the amount of hydrogen desired to be charged (pos)
#         h2_capacity = (self.h2_soc_max - self.h2_soc) / 100 * self.h2_capacity_tot # amount of h2 that can be charged till full (pos)
#         if self.h2_soc >= self.h2_soc_max:
#             self.flag = 1
#             h2_out = 0
#         else:
#             if h22charge <= h2_capacity:
#                 # enough storage capacity left to charge the desired amount of h2
#                 self.h2_soc += h22charge / self.h2_capacity_tot * 100
#                 h2_out = flow
#                 self.flag = 0
#             else:
#                 # only the available capacity can be filled with h2
#                 self.h2_soc = self.h2_soc_max
#                 self.flag = 1
#                 h2_out = h2_capacity / self.h2_charge_eff
#         self.h2_soc = round(self.h2_soc, 3)
#         re_params = {'h2_in': flow,       
#              'h2_out': h2_out,       
#              'h2_soc': self.h2_soc,          
#              'mod': 1,          
#              'flag': self.flag
#              }
#         return re_params


#     def output_flow(self, h2_gen:float) -> dict:
#         """
#         Controller that determines to charge, discharge, or do nothing based on the desired flow. Outputs the actual flow.

#         ...

#         Parameters
#         ----------
#         flow2h2storage : float
#             Desired output flow [kg/timestep]
#         Returns
#         -------
#         re_params : dict
#             Collection of parameters and their respective values
#         """
#         if h2_gen == 0:         # no action
#             # Here the state of the storage is updated in case there is no supply/demand
#             if self.h2_soc >= self.h2_soc_max:     # storage is fully charged
#                 self.flag = 1
#             elif self.h2_soc <= self.h2_soc_min:   # storage fully discharged
#                 self.flag = -1
#             else:
#                 self.flag = 0           # storage available to operate
#             h2_out = 0
#             re_params = {'h2_in': h2_gen,
#              'h2_out': h2_out,       
#              'h2_soc': self.h2_soc,          
#              'mod': 0,          
#              'flag': self.flag
#             }
#         elif h2_gen < 0:        # in case of demand
#             re_params = self.discharge(h2_gen) # storage is discharged
#         else:                           # in case of supply
#             re_params = self.charge(h2_gen) # storage is charged
#         return re_params
from illuminator.builder import ModelConstructor

class H2Storage(ModelConstructor):
    parameters = {
        'h2_soc_min': 0,  # %
        'h2_soc_max': 100,  # %
        'h2_charge_eff': 100,  # %
        'h2_discharge_eff': 100,  # %
        # 'max_h2': 10,  # kg/timestep
        # 'min_h2': 1,  # kg/timestep
        'h2_capacity_tot': 48 #kg  #2.7m3
    }
    inputs = {
        'storage_flow': 0,  # [-] 1 = charge, -1 = discharge, 0 = idle
        'flow_from_c': 0,  # [kg/timestep] flow from compressor
        'h2_flow': 0, #[kg/h] that is going to the fuel cell
        'phase_step': 0,  #of electrolyzer
        'new_density_p': 0  # new density of hydrogen at p_out and T_amb
    }
    outputs = {
        'h2_in': 0,  # kg/timestep
        'h2_flow2f': 0  # kg/timestep
    }
    states = {
        'h2_soc': 50.0,  # %
        'mod': 'idle',  # 'charge', 'discharge', or 'idle'
        'flag': 0  # 1 = full, -1 = empty, 0 = operating
    }

    time_step_size = 1  
    time = None

    def __init__(self, **kwargs) -> None:

        super().__init__(**kwargs)
        self.h2_soc = self._model.states.get('h2_soc')
        self.mod = self._model.states.get('mod')
        self.flag = self._model.states.get('flag')
        self.h2_soc_min = self._model.parameters.get('h2_soc_min')
        self.h2_soc_max = self._model.parameters.get('h2_soc_max')
        self.h2_charge_eff = self._model.parameters.get('h2_charge_eff') / 100
        self.h2_discharge_eff = self._model.parameters.get('h2_discharge_eff') / 100
        self.max_h2 = self._model.parameters.get('max_h2')
        self.min_h2 = self._model.parameters.get('min_h2')
        self.h2_capacity_tot = self._model.parameters.get('h2_capacity_tot')


    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        signal = input_data['storage_flow']
        flow = input_data['flow_from_c']
        h2_flow = input_data['h2_flow']
        phase_step = input_data['phase_step']
        new_density_p = input_data['new_density_p']

        # soc = self.states['h2_soc']
        # cap = self.parameters['h2_capacity_tot']
        # charge_eff = self.parameters['h2_charge_eff'] / 100
        # discharge_eff = self.parameters['h2_discharge_eff'] / 100
        
        h2_in = 0
        h2_out = 0
        mod = 'idle'
        flag = 0

        #With capacity in kg
        if signal == 1 or phase_step == 2 or phase_step == 3 or phase_step == 4:
            h2_in = flow
            h2_out = 0
            self.h2_soc = self.h2_soc + (h2_in * self.h2_charge_eff / self.h2_capacity_tot)*100
            mod = 'charge'
        elif signal == -1:
            h2_in = 0
            h2_out = h2_flow * (self.time_resolution / 3600)
            self.h2_soc = self.h2_soc - h2_out / self.h2_discharge_eff / self.h2_capacity_tot*100
            mod = 'discharge'

        # #With capacity in m3 and newdensity
        # if signal == 1 or phase_step == 2 or phase_step == 3 or phase_step == 4:
        #     h2_in = flow
        #     h2_out = 0
        #     self.h2_soc = self.h2_soc + (h2_in * self.h2_charge_eff / (new_density_p * self.h2_capacity_tot)) * 100
        #     mod = 'charge'
        # elif signal == -1:
        #     h2_in = 0
        #     h2_out = h2_flow * (self.time_resolution / 3600)
        #     self.h2_soc = self.h2_soc - h2_out / self.h2_discharge_eff / (new_density_p * self.h2_capacity_tot) * 100
        #     mod = 'discharge'


        elif signal == 0:
            h2_in = 0
            h2_out = 0
            self.h2_soc = self.h2_soc
            mod = 'idle'

        if self.h2_soc >= self.h2_soc_max:
            flag = 1
        elif self.h2_soc <= self.h2_soc_min:
            flag = -1

        self.set_outputs({
            'h2_in': round(h2_in, 5),
            'h2_flow2f': round(h2_out, 5)
        })
        self.set_states({
            'h2_soc': round(self.h2_soc, 3),
            'mod': mod,
            'flag': flag
        })

        return time + self.time_step_size
