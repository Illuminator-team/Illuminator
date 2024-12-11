from illuminator.builder import IlluminatorModel, ModelConstructor
import arrow


# Define the model parameters, inputs, outputs...
# TODO: Currently if a value or category isn't defined in the yaml it doesn't default to the ones below, it simply doesn't run.
battery = IlluminatorModel(
    parameters={'max_p': 150,  # maximum charging power limit (kW)
                'min_p': 250,  # maximum discharging power limit (kW)
                'max_energy': 50,  # maximum energy storage capacity of the battery (kWh)
                'charge_efficiency': 90,  # efficiency of charging the battery (%)
                'discharge_efficiency': 90,  # efficiency of discharging the battery (%)
                'soc_min': 3,  # minimum allowable state of charge for the battery (%)
                'soc_max': 80,  # maximum allowable state of charge for the battery (%)
                #'resolution': 1  # time resolution for simulation steps (seconds)
                },
    inputs={'flow2b': 0,  # power flow to/from the battery. Positive for charging, negative for discharging (kW)
            },
    outputs={'p_out': 20,  # output power from the battery after discharge/charge decision (Kw)
             'p_in': 20,  # input power to the battery (kW)
             'soc': 0,  # updated state of charge after battery operation (%)
             'mod': 0, # operation mode: 0=no action, 1=charge, -1=discharge
             'flag': -1,  # flag indicating battery status: 1=fully charged, -1=fully discharged, 0=available for control
             },
    states={'soc': 0,
            'flag': 0
            },
    time_step_size=1,
    time=None
)   

# construct the model
class Battery(ModelConstructor):
    parameters={'max_p': 150,  # maximum charging power limit (kW)
                'min_p': 250,  # maximum discharging power limit (kW)
                'max_energy': 50,  # maximum energy storage capacity of the battery (kWh)
                'charge_efficiency': 90,  # efficiency of charging the battery (%)
                'discharge_efficiency': 90,  # efficiency of discharging the battery (%)
                'soc_min': 3,  # minimum allowable state of charge for the battery (%)
                'soc_max': 80,  # maximum allowable state of charge for the battery (%)
                #'resolution': 1  # time resolution for simulation steps (seconds)
                }
    inputs={'flow2b': 0,  # power flow to/from the battery. Positive for charging, negative for discharging (kW)
            }
    outputs={'p_out': 20,  # output power from the battery after discharge/charge decision (Kw)
             'p_in': 20,  # input power to the battery (kW)
             'soc': 0,  # updated state of charge after battery operation (%)
             'mod': 0, # operation mode: 0=no action, 1=charge, -1=discharge
             'flag': -1,  # flag indicating battery status: 1=fully charged, -1=fully discharged, 0=available for control
             }
    states={'soc': 0,
            'flag': 0
            }
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        # TODO make a generalised way of doing this shit in the ModelConstructor __init__()
        super().__init__(**kwargs)
        self.max_p = self._model.parameters.get('max_p')
        self.min_p = self._model.parameters.get('min_p')
        self.max_energy = self._model.parameters.get('max_energy')
        self.charge_efficiency = self._model.parameters.get('charge_efficiency')/100
        self.discharge_efficiency = self._model.parameters.get('discharge_efficiency')/100
        self.soc_min = self._model.parameters.get('soc_min')
        self.soc_max = self._model.parameters.get('soc_max')
        #self. = self._model.parameters.get('')


    def step(self, time, inputs, max_advance=900) -> None:
        # charge the battery
        print("\nBattery")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        input_data = self.unpack_inputs(inputs)
        print("input_data: ", input_data)

        current_time = time * self.time_resolution
        print('from battery %%%%%%%%', current_time)
        eid = list(self.model_entities)[0]  # there is only one entity per simulator, so get the first entity

        print('state of charge: ', self._model.outputs['soc'])

        self._cache = {}
        # if input_data['flow2b'] != 0:
        #raghav: In this model, the input should come from the controller p_ask
        self._cache[eid] = self.output_power(input_data['flow2b'], self._model.outputs['soc'])

        # self._cache[eid] = self.entities[eid].output_power(energy_ask, self.soc[eid])          # * max_advance if trigger

        # print(self._cache[eid])
        # [p_out:,soc:,flag:]
        self._model.outputs['soc'] = self._cache[eid]['soc']
        self._model.outputs['flag'] = self._cache[eid]['flag']
        # check = list(self.soc.values())
        # check2 = check[0]  # this is so that the value that battery sends is dictionary and not a dictionary of a dictionary.
        #    out = yield self.mosaik.set_data({'Battery-0': {'Controller-0.ctrl_0': {'soc': check2}}})  # this code is supposed to hold the soc value and
        print("new state of charge:", self.soc)
        print('\n')
        return time + self._model.time_step_size

    def parse_inputs(self, inputs):
    # TODO: Move this function to model.py to unpack the inputs, for now we will keep it model specific.
        data = {}
        for attrs in inputs.values():
            for attr, sources in attrs.items():
                values = list(sources.values())  # we expect each attribute to just have one sources (only one connection per input)
                if len(values) > 1:
                    raise RuntimeError(f"Why are you passing multiple values {value}to a single input? ")
                data[attr] = values[0]
        return data
    

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
        hours = self.time_resolution / 60 / 60
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
        hours = self.time_resolution / 60 / 60
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

if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    battery_model = Battery(battery)

    print(battery_model.step(1))