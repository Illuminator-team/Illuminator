class Controller_Congestion:

    # make adaptable with different combinations of RES generation and
    def __init__(self, soc_min=None, soc_max=None, max_p=None, gridconnect_ctrl = None):
        self.res_load = 0
        if soc_min != None and soc_max != None:
            self.soc_max_b = soc_max
            self.soc_min_b = soc_min
            self.max_p_b = max_p  # maximum power of battery
            self.bat_active = 1
        else:
            self.bat_active = 0

        if gridconnect_ctrl != None:
            self.limit_grid_connect = gridconnect_ctrl * 0.7
            print('connection limit_:' + str(self.limit_grid_connect))

        self.dump = 0
        self.flow_b = 0  # flow_b is the flow to the battery so negative when discharge, positive when charge
        # looking at the battery model the flow_b is the power flow
        self.load_shift = 0

    def control(self, wind_gen, pv_gen, load_dem, soc=None, load_EV=None, load_HP=None, flag_warning = None,
                ):
        # reset flow2b
        self.flow_b = 0
        self.soc_b = soc
        print('flag warning: ' + str(flag_warning))
        print('Load dem: ' + str(load_dem))
        print('pv: ' + str(pv_gen))
        print('wind: ' + str(wind_gen))

        # still need to include how load_shift gets added if flag does not give warning

        if load_EV != None:
            if load_HP != None:
                self.res_load = load_dem + load_EV + load_HP - wind_gen - pv_gen  # kW


            else:
                self.res_load = load_dem + load_EV - wind_gen - pv_gen


        elif load_HP != None:
            self.res_load = load_dem + load_HP - wind_gen - pv_gen

        else:
            self.res_load = load_dem - wind_gen - pv_gen  # kW

        if self.res_load < self.limit_grid_connect:
            extra_load_allowed = min(self.limit_grid_connect-self.res_load,self.limit_grid_connect)
            additional_load = min(extra_load_allowed, self.load_shift)
            print('additional load: ' + str(additional_load))
            self.res_load = self.res_load + additional_load
            self.load_shift -= additional_load

        if self.bat_active == 1:
            if self.res_load > 0:
                # demand not satisfied -> discharge battery if possible
                if self.soc_b > self.soc_min_b:  # checking if soc is above minimum
                    print('Discharge Battery')
                    max_discharge = (self.soc_b - self.soc_min_b) / 100 * self.max_p_b
                    print(f'max discharge: {max_discharge}')
                    print(f'res load: {self.res_load}')
                    self.flow_b = -min(self.res_load, max_discharge)
                    print('Flow Bat: ' + str(self.flow_b))
                    # self.soc_b = self.soc_b + self.flow_b soc is not updated in controller

            elif self.res_load < 0:

                if self.soc_b < self.soc_max_b:
                    print('Charge Battery')
                    max_flow2b = ((self.soc_max_b - self.soc_b) / 100) * self.max_p_b  # Energy flow in kW
                    self.flow_b = min((-self.res_load), max_flow2b)
                    print('Flow Bat: ' + str(self.flow_b))
                    print('Excess generation that cannot be stored: ' + str(-self.res_load - self.flow_b))

            else:
                print('No Residual Load, RES production exactly covers demand')
                self.flow_b = 0
                self.dump = 0
                # demand_res = residual_load

            # update residual load with battery discharge/charge
            # self.res_load = self.res_load + self.flow_b
            self.dump = -(self.res_load + self.flow_b)
        else:
            self.dump = - self.res_load

        if flag_warning == 1:
            print('enter flag condition')
            overload = (-self.dump) - self.limit_grid_connect
            self.load_shift += min(overload, load_HP + load_EV)
            print('load_not_yet: ' + str(self.load_shift))
            if overload > 0:
                print('update dump')
                self.dump = -self.limit_grid_connect

        print('residual load: ' + str(self.res_load))
        print('battery flow: ' + str(self.flow_b))
        print('dump: ' + str(self.dump))
        # if self.bat_active == 1:
        re_params = {'flow2b': self.flow_b, 'res_load': self.res_load, 'dump': self.dump}
        # else:
        # re_params = {'res_load': self.res_load,'dump': self.dump}
        return re_params