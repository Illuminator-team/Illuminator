# class eboiler_python:
#
#     def __init__(self, eff):
#         self.q_gen = 0
#         self.eff = eff
#
#     def demand(self, eboiler_dem):
#         # incoming eboiler is in kWh at every 15 min interval
#         # incoming value of eboiler is in kWh
#
#         self.q_gen = self.eff * eboiler_dem
#         re_params = {'eboiler_dem':eboiler_dem, 'q_gen': self.q_gen}
#         return re_params


class eboiler_python:
    def __init__(self, eboiler_set):
        # Capacity of the boiler in kW
        self.capacity = eboiler_set['capacity']

        # kW
        self.min_load = eboiler_set['min_load']
        self.max_load = eboiler_set['max_load']

        # Standby loss as a fraction of the capacity
        self.standby_loss = eboiler_set['standby_loss']

        # Efficiency under maximum load
        self.efficiency_under_max_load = eboiler_set['efficiency_under_max_load']
        self.resolution=eboiler_set['resolution']

    def demand(self, eboiler_dem):
        # Check if the electricity input is within the operation limits
        if  eboiler_dem< self.min_load:
            electricity_input=0
        elif eboiler_dem> self.max_load:
            electricity_input=self.max_load
        else:
            electricity_input=eboiler_dem

        # Calculate the efficiency as a function of the load
        load = electricity_input / self.capacity
        efficiency = self.efficiency_under_max_load * load

        # Calculate the heat generated and the standby loss
        heat_generated = efficiency * electricity_input
        standby_loss = self.standby_loss * self.capacity

        return {
            'eboiler_dem':eboiler_dem,
            'electricity_consumed': electricity_input,
            'heat_generated': heat_generated,
            'standby_loss': standby_loss
        }
