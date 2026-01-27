from illuminator.builder import IlluminatorModel, ModelConstructor

class Hydrogen_production_controller(ModelConstructor):
    """
    Hydrogen Production Controller for Hydrogen System Management.

    This controller manages the operation of a hydrogen system, including
    the discharge of a hydrogen buffer and the adjustment of production setpoints
    based on electricity prices or state of charge.

    System Setup (as defined in Hydrogen_production.yaml):
    ------------------------------------------------------
    In the 'Hydrogen_system_4' scenario, the controller coordinates:
    - Thermolyzer (thermolyzer1): Primary production unit using biomass 
      (from 'CSVbiomass'). Its 'desired_out' is controlled by 'Thermolyzer_setpoint'.
    - ZZE Buffer (ZZE1): Storage unit. Its 'setpoint' is controlled by 
      'ZZE_setpoint', and it feeds back its 'soc'.
    - Price Feed (CSVdayahead): Provides 'DayAhead_price' for market-based control.
    - Downstream: Production and storage flows are merged in 'Joint1' and 
      purified in 'PSA1'.

    Parameters
    ----------
    (none)

    Inputs
    ----------
    ZZE_soc : float
        State of charge of the ZZE buffer [%].
    DayAhead_price : float
        Day-ahead electricity price [EUR/MWh].
    
    Outputs
    ----------
    (none)

    States
    ----------
    Thermolyzer_setpoint : float
        Current setpoint for thermolyzer production [kg/h].
    ZZE_setpoint : float
        Current hydrogen output from the ZZE buffer [kg/h].
    """
    time_step_size=1
    time=0

    # init function to set up the controller, is only called once at the start of the simulation
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.discharge_counter = 3600  # Initialize discharge counter to 1 hour (3600 seconds)
        self.discharging = False  # Initialize discharging state to False
        self.thermolyzer_setpoint = 100  # Set initial setpoint for thermolyzer production
        self.zze_setpoint = 0  # Initialize ZZE hydrogen output to 0


    def step(self, time, inputs, max_advance=1) -> None:

        # get input data
        input_data = self.unpack_inputs(inputs)
        zze_soc = input_data['ZZE_soc']
        price = input_data['DayAhead_price']

        # If discharging session is going on
        if self.discharging:
            self.discharge_counter -= self.time_step_size * self.time_resolution
            if self.discharge_counter <= 0:
                self.discharging = False
        
        # If there is no active discharging session
        else:
            # If the battery should be discharged
            if price > 130:  # check if ZZE buffer is above 60% SOC
                self.thermolyzer_setpoint = 30  # set thermolyzer production to 30 kg/h
                self.zze_setpoint = -2 # set ZZE buffer hydrogen to discharge at 0.5kg/h
                self.discharging = True
                self.discharge_counter = 3600*9  # reset discharge counter to 1 hour (3600 seconds)

            # If the battery should be charged
            elif price < 120:
                self.thermolyzer_setpoint = 31.5  # set thermolyzer production to 31.5 kg/h
                self.zze_setpoint = 2 # start charging ZZE buffer hydrogen

            else: # don't charge, don't discharge
                self.thermolyzer_setpoint = 31.5  # set thermolyzer production to 31.5 kg/h
                self.zze_setpoint = 0 # don't charge ZZE buffer hydrogen

        # set the states to send the data to the other models
        self.set_states({
            'Thermolyzer_setpoint': self.thermolyzer_setpoint,
            'ZZE_setpoint': self.zze_setpoint,
        })
        
        return time + self._model.time_step_size


    # step function, called every time step to update
    def step_simple(self, time, inputs, max_advance=1) -> None:

        # get input data
        input_data = self.unpack_inputs(inputs)
        zze_soc = input_data['ZZE_soc']

        # If discharging session is going on
        if self.discharging:
            self.discharge_counter -= self.time_step_size * self.time_resolution
            if self.discharge_counter <= 0:
                self.discharging = False
        
        # If there is no active discharging session
        else:
            # If the battery should be discharged
            if zze_soc >= 80:  # check if ZZE buffer is above 60% SOC
                self.thermolyzer_setpoint = 30  # set thermolyzer production to 30 kg/h
                self.zze_setpoint = -2 # set ZZE buffer hydrogen to discharge at 0.5kg/h
                self.discharging = True
                self.discharge_counter = 3600*9  # reset discharge counter to 1 hour (3600 seconds)

            # If the battery should not be discharged
            else:
                self.thermolyzer_setpoint = 31.5  # set thermolyzer production to 31.5 kg/h
                self.zze_setpoint = 2 # start charging ZZE buffer hydrogen

        # set the states to send the data to the other models
        self.set_states({
            'Thermolyzer_setpoint': self.thermolyzer_setpoint,
            'ZZE_setpoint': self.zze_setpoint,
        })
        
        return time + self._model.time_step_size