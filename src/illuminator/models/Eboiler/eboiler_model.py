class eboiler_python:
    # Need to check if used in DNcontrol or multienergy
    def __init__(self, eboiler_set:dict) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the controller_mosaik.controlSim class.
        
        ...

        Parameters
        ----------
        eboiler_set : dict
            The collection of the boiler settings
        
        Attributes
        ----------
        self.capacity : ???  
            Capacity of the boiler in kW, converting to W
        self.min_load : ???  
            Minimum load in kW, converting to W
        self.max_load : ???  
            Maximum load in kW, converting to W
        self.standby_loss : ???  
            Standby loss as a fraction of the capacity
        self.efficiency : ???  
            Efficiency under maximum load
        self.resolution : ???
            Resolution of the system
        """
        self.capacity = eboiler_set['capacity']  # Capacity of the boiler in kW, converting to W
        self.min_load = eboiler_set['min_load']  # Minimum load in kW, converting to W
        self.max_load = eboiler_set['max_load']  # Maximum load in kW, converting to W
        self.standby_loss = eboiler_set['standby_loss']  # Standby loss as a fraction of the capacity
        self.efficiency = eboiler_set['efficiency']  # Efficiency under maximum load
        self.resolution = eboiler_set['resolution']  # Resolution of the system

    def demand(self, eboiler_dem:dict) -> dict:
        """
        Calculates the demand of the electric boiler based on the input demand and heat source temperature.

        ...

        Parameters
        ----------
        inputs : dict 
            Electric boiler demand data. 
            {'Q_Demand': (heat demand in W), 'heat_source_T' : (temperature in °C)}

        Returns
        -------
        dict
            Returns electric boiler data on the heat supplied and electricity consumed.
        """
        Q_Demand = eboiler_dem
        #heat_source_T = inputs['heat_source_T']

        # Convert Q_Demand from W to kW for calculations
        Q_Demand_kW = Q_Demand #/ 1000.0
        standby_loss = self.standby_loss * self.capacity  # Standby loss in kW
        power_require = (Q_Demand_kW+standby_loss)/self.efficiency

        # Check if the electricity input is within the operation limits
        if power_require < self.min_load:
            electricity_input = 0
        elif power_require > self.max_load:
            electricity_input = self.max_load
        else:
            electricity_input = power_require


        # Calculate the heat supplied in kW (considering standby loss) and convert it back to W
        Q_supply = (electricity_input - standby_loss) * self.efficiency*1000  # Converting from kW to W

        return {
            'eboiler_dem':eboiler_dem,
            #'heat_source_T':heat_source_T,
            'q_gen': Q_supply,
            'e_consumed': electricity_input * 1000,  # Converting from kW to W
            'standby_loss':standby_loss * 1000
        }

