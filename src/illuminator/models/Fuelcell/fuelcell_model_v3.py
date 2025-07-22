# from illuminator.builder import ModelConstructor

# class Fuelcell(ModelConstructor):
    # """
    # A class to represent a Fuelcell model.
    # This class provides methods to simulate the operation of a fuelcell.

    # Attributes
    # ----------
    # parameters : dict
    #     Dictionary containing fuelcell parameters such as efficiency, maximum hydrogen input flow, and minimum hydrogen input flow.
    # inputs : dict
    #     Dictionary containing input variables like hydrogen flow to the fuelcell.
    # outputs : dict
    #     Dictionary containing calculated outputs like power output.
    # states : dict
    #     Dictionary containing the state variables of the fuelcell model.
    # time_step_size : int
    #     Time step size for the simulation.
    # time : int or None
    #     Current simulation time.
    # hhv : float
    #     Higher heating value of hydrogen [kJ/mol].
    # mmh2 : float
    #     Molar mass of hydrogen (H2) [gram/mol].

    # Methods
    # -------
    # step(time, inputs, max_advance=900)
    #     Simulates one time step of the fuelcell model.
    # power_out(h2_flow2f)
    #     Calculates the power output of the fuelcell.
    # """
    # parameters={
    #         'fuelcell_eff': 99,     # fuelcell efficiency [%]
    #         'h2_max' : 10,          # max hyrogen input flow [kg/timestep]  
    #         'h2_min' : 0,           # min hydrogen input flow [kg/timestep]
    #         'max_p_out' : 1,        # maximum power output [kW]
    #         'max_ramp_up' : 10      # maximum ramp up in power per timestep [kW/timestep] 
    # },
    # inputs={
    #         'h2_flow2f' : 0         # hydrogen flow to the fuelcell [kg/timestep]
    # },
    # outputs={
    #         'p_out' : 0             # power output [kW]
    # },
    # states={},

    # # other attributes
    # time_step_size=1,
    # time=None
    # hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    # mmh2 = 2.02                 # molar mass hydrogen (H2) [g/mol]
 
    # def __init__(self, **kwargs) -> None:
    #     """
    #     Initialize the Fuelcell model with the provided parameters.

    #     Parameters
    #     ----------
    #     kwargs : dict
    #         Additional keyword arguments to initialize the model.
    #     """
    #     super().__init__(**kwargs)
    #     self.fuelcell_eff = self._model.parameters.get('fuelcell_eff')
    #     self.h2_max = self._model.parameters.get('h2_max')
    #     self.h2_min = self._model.parameters.get('h2_min')
    #     self.max_ramp_up = self._model.parameters.get('max_ramp_up')
    #     self.max_p_out = self._model.parameters.get('max_p_out')
    #     self.p_in_last = 0  # Indicator of the last power input initialized to be 0 

    # def step(self, time: int, inputs: dict=None, max_advance: int = 900) -> None:
    #     """
    #     Simulates one time step of the fuelcell model.

    #     This method processes the inputs for one timestep, updates the fuelcell state based on
    #     the hydrogen flow, and sets the model outputs accordingly.

    #     Parameters
    #     ----------
    #     time : int
    #         Current simulation time
    #     inputs : dict
    #         Dictionary containing input values, specifically:
    #         - h2_flow2f: Hydrogen flow to the fuelcell in kg/timestep
    #     max_advance : int, optional
    #         Maximum time step size (default 900)

    #     Returns
    #     -------
    #     int
    #         Next simulation time step
    #     """

    #     # print("\nFuelcell:")
    #     # print("inputs (passed): ", inputs)
    #     # print("inputs (internal): ", self._model.inputs)
    #     # get input data 
    #     input_data = self.unpack_inputs(inputs)
    #     print("input data: ", input_data)
    #     current_time = time * self.time_resolution
    #     print('from fuelcell %%%%%%%%%%%', current_time)
    #     self._model.outputs['p_out'] = self.power_out(input_data['h2_flow2f'], max_advance)
    #     print("outputs:", self.outputs)
        
    #     return time + self._model.time_step_size
        
    # def power_out(self, h2_flow2f: float, max_advance: int) -> float:
    #     """
    #     Calculates the output power of the fuelcell

    #     ...

    #     Parameters
    #     ----------
    #     h2_flow2f : float
    #         H2 flow into the fuelcell [kg/timestep]

    #     Returns
    #     -------
    #     p_out : float
    #         The outout power of the fuelcell [kW]
    #     """
    #     # limit hydrogen consumption by the minimum and maximum hydrogen the fuelcell can accept
    #     h2_flow = max(self.h2_min, min(self.h2_max, h2_flow2f))         # [kg/timestep]
    #     h2_flow = h2_flow / max_advance                                 # [kg/s]
    #     p_out = (h2_flow * self.fuelcell_eff * self.hhv) / self.mmh2    # [kW]
    #     p_out = min(p_out, self.max_p_out)                               # limit power output by the max power output [kW]
    #     p_out = self.ramp_lim(p_out, max_advance)                       # considering ramp limits [kW]
    #     return p_out

    # def ramp_lim(self, p_out, max_advance):
    #     """
    #     Limits the power output ramp rate of the fuelcell.

    #     ...

    #     Parameters
    #     ----------
    #     p_out : float
    #         Desired power output [kW]
    #     max_advance : int
    #         Maximum time step size

    #     Returns
    #     -------
    #     power_out : float
    #         Adjusted power output [kW] after applying ramp rate limits
    #     """
    #     # restrict the power input to not increase more than max_p_ramp_rate
    #     # compared to the last timestep
    #     p_change = p_out - self.p_in_last
    #     if abs(p_change) > self.max_ramp_up:
    #         if p_change > 0:
    #             power_out = self.p_in_last + self.max_ramp_up * max_advance
    #         else:
    #             power_out = self.p_in_last - self.max_ramp_up * max_advance
    #     else:
    #         power_out = p_out
    #     self.p_in_last = power_out
    #     return power_out
from illuminator.builder import ModelConstructor

class Fuelcell(ModelConstructor):

    parameters = {
        'fuelcell_eff': 39.78,  # %
        'ramp_up_time1': 40, # s from 0 W to 500 W
        'ramp_up_power1': 0.5, # kW at the end of ramp_up_time1
        'ramp_up_time2': 60, # s from 500 W to 1000 W
        'ramp_down_time': 60, # s from 1.623 kW to 0 W
        'max_p_out': 1.83,      # kW
        'h2_in': 0.002040276 #kg/min and 22.7 NL/min
    }
    inputs = {
        'run_fuelcell': 0,   # signal
        # 'h2_flow2f': 0       # kg/timestep
    }
    outputs = {
        'p_out_fuelcell': 0,
        # 'p_out_fuelcell_controller': 0,  # kW
        'p_out_fuelcell_grid': 0 # kW, power output to the grid
    }
    states = {
        'h2_flow': 0, #kg/h
        'fc_status': 'off',  # 'off', 'ramp_up1', 'ramp_up2', 'on', 'ramp_down
        # 'timer': 0  # Timer for fuelcell warmup
        'phase_step': 0  # 0: off, 1: ramp_up1, 2: ramp_up2, 3: on, 4: ramp_down
    }

    time_step_size = 1  
    time = None

    hydrogen_energy_content = 33.33 # kWh/kg at 1 atm
    hhv = 141.9  # kJ/mol
    mmh2 = 2.016  # g/mol

    def __init__(self, **kwargs) -> None:

        super().__init__(**kwargs)
        self.fuelcell_eff = self._model.parameters.get('fuelcell_eff')  
        self.ramp_up_time1 = self._model.parameters.get('ramp_up_time1')
        self.ramp_up_power1 = self._model.parameters.get('ramp_up_power1')
        self.ramp_up_time2 = self._model.parameters.get('ramp_up_time2')
        self.ramp_down_time = self._model.parameters.get('ramp_down_time')
        self.max_p_out = self._model.parameters.get('max_p_out')
        self.h2_in = self._model.parameters.get('h2_in')
        self.h2_flow = self._model.states.get('h2_flow')
        # self.fc_status = self._model.states.get('fc_status')
        # self.timer = self._model.states.get('timer')
        self.phase_step = self._model.states.get('phase_step')

        self.phase_start_time = None


    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        run_fc = input_data['run_fuelcell']
        dt_h = self.time_resolution / 3600
        self.time = time
        # flow2f = 0
        p_out = 0
        # self.h2_flow = 0
        # hourflow2f = 0

        if run_fc ==1:
            p_out = self.h2_in*60 * self.hydrogen_energy_content * (self.fuelcell_eff/100) #kW
            self.h2_flow = self.h2_in * 60

        if run_fc ==0:
            p_out = 0
            self.h2_flow = 0 


        # if run_fc == 1:
        #     if self.phase_step == 3:
        #         self.phase_step = 0 #als in de ramping down fase de fuel cell weer word aangezet is de phase_step nog 3 en blijft p_out op 0
        #     if self.phase_step == 0: #start ramping up
        #         if self.phase_start_time is None:
        #             self.phase_start_time = time  # Set once
        #         elapsed = (time - self.phase_start_time) * self.time_resolution
        #         ramp_fraction = min(elapsed / self.ramp_up_time1, 1.0)
        #         p_out = ramp_fraction * self.ramp_up_power1
        #         self.h2_flow = p_out * self.h2_flow_max / self.max_p_out
        #         if elapsed >= self.ramp_up_time1:
        #             self.phase_step = 1
        #             self.phase_start_time = time  # Reset for next ramp phase

        #     elif self.phase_step == 1:
        #         elapsed = (time - self.phase_start_time) * self.time_resolution
        #         ramp_fraction = min(elapsed / self.ramp_up_time2, 1.0)
        #         p_out = self.ramp_up_power1 + ramp_fraction * (self.max_p_out - self.ramp_up_power1)
        #         self.h2_flow = p_out * self.h2_flow_max / self.max_p_out

        #         if elapsed >= self.ramp_up_time2:
        #             self.phase_step = 2
        #             self.phase_start_time = time

        #     elif self.phase_step == 2:
        #         p_out = self.max_p_out
        #         self.h2_flow = self.h2_flow_max

        # elif run_fc == 0:
        #     if self.phase_step == 2:
        #         self.phase_step = 3
        #         self.phase_start_time = time

        #     if self.phase_step == 3:
        #         elapsed = (time - self.phase_start_time) * self.time_resolution
        #         ramp_fraction = max(1 - (elapsed / self.ramp_down_time), 0)
        #         p_out = ramp_fraction * self.max_p_out
        #         self.h2_flow = p_out * self.h2_flow_max / self.max_p_out

        #         if elapsed >= self.ramp_down_time:
        #             self.phase_step = 0
        #             self.phase_start_time = None
        #             # p_out = 0
        #             # self.h2_flow = 0

            # elif self.phase_step == 0:
            #     p_out = 0
            #     self.h2_flow = 0

        self.set_outputs({
            'p_out_fuelcell': round(p_out, 3),
            # 'p_out_fuelcell_controller': round(p_out, 3),  # Assuming controller output is same as fuelcell output
            'p_out_fuelcell_grid': round(p_out, 3)  # Assuming all power goes to the grid
        })

    
        self.set_states({
            'h2_flow': self.h2_flow,
            # 'fc_status': self.fc_status,
            'phase_step': self.phase_step
            # 'timer': self.timer
        })

        return time + self._model.time_step_size
    
     
        # # === Phase Logic ===
        # if self.fc_status == 'off':
        #     if run_fc == 1:
        #         self.fc_status = 'ramp_up1'
        #         self.timer = time

        # elif self.fc_status == 'ramp_up1':
        #     elapsed = time - self.timer
        #     ramp_fraction = min(elapsed / self.ramp_up_time1, 1.0)
        #     p_out = ramp_fraction * self.ramp_up_power1
        #     hourflow2f = ramp_fraction * self.h2_flow_max * (self.ramp_up_power1 / self.max_p_out)
        #     # flow2f = h2_flow2f

        #     if elapsed >= self.ramp_up_time1:
        #         self.fc_status = 'ramp_up2'
        #         self.timer = time

        # elif self.fc_status == 'ramp_up2':
        #     elapsed = time - self.timer
        #     ramp_fraction = min(elapsed / self.ramp_up_time2, 1.0)
        #     p_out = self.ramp_up_power1 + ramp_fraction * (self.max_p_out - self.ramp_up_power1 )
        #     hourflow2f = (self.ramp_up_power1 + ramp_fraction * (self.max_p_out - self.ramp_up_power1 )) * self.h2_flow_max / self.max_p_out
        #     # flow2f = h2_flow2f
        #     if elapsed >= self.ramp_up_time2:
        #         self.fc_status = 'on'
        #         self.timer = time

        # elif self.fc_status == 'on':
        #     p_out = self.max_p_out
        #     hourflow2f = self.h2_flow_max
        #     # flow2f = h2_flow2f
        #     if run_fc == 0:
        #         self.fc_status = 'ramp_down'
        #         self.timer = time

        # elif self.fc_status == 'ramp_down':
        #     elapsed = time - self.timer
        #     ramp_fraction = max(1 - (elapsed / self.ramp_down_time), 0)
        #     p_out = ramp_fraction * self.max_p_out
        #     hourflow2f = ramp_fraction * self.h2_flow_max
        #     # flow2f = h2_flow2f * ramp_fraction
        #     if elapsed >= self.ramp_down_time:
        #         self.fc_status = 'off'
        #         self.timer = time
