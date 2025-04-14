class grid_connection_python():

    def __init__(self, connection_capacity, tolerance_limit, critical_limit):
        self.connection_capacity = connection_capacity
        self.tolerance_limit = tolerance_limit
        self.critical_limit = critical_limit
        self.flag_critical = 0
        self.flag_warning = 0

    def check_limits(self, dump):
        #dump = power to the grid in kW

        if (-dump >= (self.critical_limit * self.connection_capacity) or
                dump <= -(self.critical_limit * self.connection_capacity)):
            self.flag_critical = 1
            self.flag_warning = 1
        elif (-dump >= (self.tolerance_limit * self.connection_capacity) or
              dump <= -(self.tolerance_limit * self.connection_capacity)):
            self.flag_critical = 0
            self.flag_warning = 1
        else:
            self.flag_critical = 0
            self.flag_warning = 0
        re_params = {'flag_critical': self.flag_critical, 'flag_warning': self.flag_warning}
        return re_params