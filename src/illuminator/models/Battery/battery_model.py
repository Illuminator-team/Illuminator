import datetime
import pandas as pd
import matplotlib.pyplot as plt

# sign convension: -ve means discharge, +ve means Charge

class BatteryModel:
    #'battery_set',#max_p,min_p,max_energy,charge_efficiency,discharge_efficiency
                              #soc_min,soc_max,flag, resolution
    #'initial_set',  # initial_soc

    def __init__(self, initial_set:dict, battery_set:dict) -> None:  
        """
        Used in Python based Mosaik simulations as an addition to the battery_mosaik.BatteryholdSim class.

        ...

        Parameters
        ----------
        initial_set : dict
            ???
        battery_set : dict
            ???

        Attributes
        ----------
        self.soc : int
            The current state of charge (SOC)
        self.powerout : int 
            ???
        self.soc_min : int 
            The minimum state of charge (SOC)
        self.soc_max : int 
            The maximum state of charge (SOC)
        self.max_p : int(?) 
            (???) represented in kW
        self.min_p : int(?) 
            (???) represented in kW
        self.max_energy : int(?)  
            (???) represented in kWh
        self.charge_efficiency : ???  
            ???
        self.discharge_efficiency : ???
            ???
        self.flag : ???
            ???
        self.resolution : ???
            ???
        """
        # this is called a method (since it is basically a function)
  #  by using '__int__' we are making our own constructor. This helps us to pass all the attributes we want to the
  # object that is instantiated.
  # 'self' refers to the object calling it. Eg: If we want an object BatteryModel-1,
  #     self helps in connecting this object with the attributes under __init__()
  # everything in the bracket is a parameter. We provide aruguments (or values) for them.
        self.soc = initial_set['initial_soc']
        # self.i_soc = initial_set['initial-soc'] #########################################################
# for every object we create, soc is the attribute it gets with a value we provide.
        self.powerout = 0  # an attribute
        self.soc_min = battery_set['soc_min']  # an attribute
        self.soc_max = battery_set['soc_max']  # an attribute
        self.max_p = battery_set['max_p']  # kW  # an attribute
        self.min_p = battery_set['min_p']  # kW  # an attribute
        self.max_energy = battery_set['max_energy']  # kWh  # an attribute
        self.charge_efficiency = battery_set['charge_efficiency']  # an attribute
        self.discharge_efficiency = battery_set['discharge_efficiency']  # an attribute
        self.flag = battery_set['flag']  # an attribute
        self.resolution = battery_set['resolution']  # minitues  #an attribute



    # this method is called from the output_power method when conditions are met.
    def discharge_battery(self, flow2b:int) -> dict:  #flow2b is in kw
        """
        Discharge the battery, calculate the state of charge and return parameter information

        ...

        Parameters
        ----------
        flow2b : int
            (???) in kW
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        hours = self.resolution / 60
        flow = max(self.min_p, flow2b)
        if (flow < 0):
            energy2discharge = flow * hours / self.discharge_efficiency  # (-ve)
            energy_capacity = ((self.soc_min - self.soc) / 100) * self.max_energy
            if self.soc <= self.soc_min:
                self.flag = -1
                self.powerout = 0
            else:
                if energy2discharge > energy_capacity:
                    # more than enough energy to discharge
                    # Check if minimum energy of the battery is reached -> Adjust power if necessary
                    self.soc = self.soc + (energy2discharge / self.max_energy * 100)
                    self.powerout = flow
                    self.flag = 0  # Set flag as ready to discharge or charge

                else:  # Fully-discharge Case
                    self.powerout = energy_capacity / self.discharge_efficiency / hours
                    # warn('\n Home Battery is fully discharged!! Cannot deliver more energy!')
                    self.soc = self.soc_min
                    self.flag = -1  # Set flag as 1 to show fully discharged state
        self.soc = round(self.soc, 3)
        re_params = {'p_out': self.powerout,
                        # 'energy_drain': output_show,
                        # 'energy_consumed': 0,
                        'p_in': flow,
                        'soc': self.soc,
                        'mod': -1,
                        'flag': self.flag}
                        #'i_soc': self.i_soc}

        # here we are returning the values of these parameters which will be needed by another python model
        return re_params

    def charge_battery(self, flow2b:int) -> dict:
        """
        Charge the battery, calculate the state of charge and return parameter information

        ...

        Parameters
        ----------
        flow2b : int
            (???) in kW
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        hours = self.resolution / 60
        flow = min(self.max_p, flow2b)
        if (flow > 0):
            energy2charge = flow * hours * self.charge_efficiency  # (-ve)
            energy_capacity = ((self.soc_max - self.soc) / 100) * self.max_energy
            if self.soc >= self.soc_max:
                self.flag = 1
                self.powerout = 0
            else:
                if energy2charge <= energy_capacity:
                    self.soc = self.soc + (energy2charge / self.max_energy * 100)
                    self.powerout = flow
                    self.flag = 0  # Set flag as ready to discharge or charge

                else:  # Fully-charge Case
                    self.powerout = energy_capacity / self.charge_efficiency / hours
                    # warn('\n Home Battery is fully discharged!! Cannot deliver more energy!')
                    self.soc = self.soc_max
                    self.flag = 1  # Set flag as 1 to show fully discharged state
        self.soc = round(self.soc, 3)
        re_params = {'p_out': self.powerout,
                        # 'energy_consumed': output_show,
                        # 'energy_drain': 0,
                        'p_in': flow,
                        'soc': self.soc,
                        'mod': 1,
                        'flag': self.flag}

        return re_params


# this method is like a controller which calls a method depending on the condition.
# first, this is checked. As per the p_ask and soc, everything happens.
# p_ask and soc are the parameters whos values we have to provide when we want to create an object of this class. i.e,
    # when we want to make a battery model.
    def output_power(self, flow2b:int, soc:int) -> dict:#charging power: positive; discharging power:negative
        """
        Gives information depending on the current flow2b and soc value.
        If there is no power demand it gives in current battery state of charge information.
        If there is a negative demand for power then it discharged the battery. Alternatively it charges the battery.
        
        ...

        Parameters
        ----------
        flow2b : int
            ???
        soc : int
            The current state of charge (SOC)

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        self.soc = soc  # here we assign the value of soc we provide to the attribute self.soc
        data_ret = {}
        # {'p_out',
        # 'soc',
        # 'mod',  # 0 = noaction,1 = charge,-1=discharge
        # 'flag',} # 1 means full charge, -1 means full discharge, 0 means available for control
    # conditions start:
        if flow2b == 0:  # i.e when there isn't a demand of power at all,

            # soc can never exceed the limit so when it is equal to the max, we tell it is completely charged
            if self.soc >= self.soc_max:
                self.flag = 1  # meaning battery object we created is fully charged

            # soc can never exceed the limit so when it is equal to the min, we tell it is completely discharged
            elif self.soc <= self.soc_min:
                self.flag = -1

            # if the soc is between the min and max values, it is ready to be discharged or charged as per the situation
            else:
                self.flag = 0  # meaning it is available to operate.

            # here we are sending the current state of the battery
            re_params={'p_out': 0,
                       # 'energy_drain': 0,
                       # 'energy_consumed': 0,
                       'p_in': 0,
                        'soc': self.soc,
                        'mod': 0,
                        'flag': self.flag}
        else:
            # if the p_ask is a -ve value, it means battery needs to discharge.
            if flow2b < 0:  #discharge

                # Can the battery discharge or not depends on the current state of the battery for which we call the
                # method discharge_battery. If the p_ask < 0 condition is met, the program directly goes the method.
                re_params = self.discharge_battery(flow2b)

            # other option is for p_ask to be > 0 which means we need to charge.
            else:

                # Can the battery charge depends on the current state of the battery for which we call the
                # method charge_battery. If the p_ask > 0 condition is met, the program directly goes the method.
                re_params = self.charge_battery(flow2b)


        return re_params
    # conditions end

# if __name__=='__main__':
#     initial_set={'initial_soc':50}
#     Battery_set = {'max_p': 2, 'min_p': -2, 'max_energy': 10,
#                    'charge_efficiency': 0.9, 'discharge_efficiency': 0.9,
#                    'soc_min': 10, 'soc_max': 90, 'flag': 0, 'resolution': 15}
#
#
#     #max_p,min_p,max_energy,charge_efficiency,discharge_efficiency
#                               #soc_min,soc_max,flag, resolution
#     Model=BatteryModel(initial_set,Battery_set)
#     Model.charge_battery(0.1)
#     Model.discharge_battery(-0.1)
#     Model.output_power(0.1,95)
#     Model.output_power(-0.1,95)







