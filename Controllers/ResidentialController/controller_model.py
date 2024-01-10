
class controller_python:
    def __init__(self, soc_min, soc_max, h2_soc_min, h2_soc_max, fc_eff):
        self.soc_max_b = soc_max
        self.soc_min_b = soc_min
        self.soc_max_h2 = h2_soc_max
        self.soc_min_h2 = h2_soc_min
        self.fc_eff = fc_eff

        self.dump = 0
        self.flow_b = 0
        self.flow_e = 0
        self.fc_out = 0

    def control(self, wind_gen, pv_gen, load_dem, soc, h2_soc):#, fc_gen):
    # def control(self,soc , pv_gen, load_dem, wind_gen):

        self.soc_b = soc
        self.soc_h = h2_soc
        flow = wind_gen + pv_gen - load_dem  # kW

        if flow < 0:  # means that the demand is not completely met and we need support from battery and fuel cell
            if self.soc_b > self.soc_min_b:  # checking if soc is above minimum. It can be == to soc_max as well.
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0

            elif self.soc_b <= self.soc_min_b:
                self.flow_b = 0
                self.flow_e = 0
                q = 39.4
                self.h_out = (flow / q) / self.fc_eff

                print('Battery Discharged')


        elif flow > 0:  # means we have over generation and we want to utilize it for charging battery and storing hydrogen
            if self.soc_b < self.soc_max_b:
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0
            elif self.soc_b == self.soc_max_b:
                self.flow_b = 0
                if self.soc_h < self.soc_max_h2:
                    self.flow_e = flow
                    self.dump = 0
                    self.h_out = 0
                elif self.soc_h == self.soc_max_h2:
                    self.flow_e = 0
                    self.dump = flow
                    self.h_out = 0

        re_params = {'flow2b': self.flow_b, 'flow2e': self.flow_e, 'dump': self.dump, 'h2_out':self.h_out}
        return re_params
