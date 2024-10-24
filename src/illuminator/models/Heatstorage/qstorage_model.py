# compressed hydrogen storage tank at 700bar and storing about 100kg of hydrogen
import numpy as np
class heatstorage_python:
    def __init__(self, soc_init, max_temperature, min_temperature, insulation, ext_temp, therm_cond,
                 length, diameter, density, c, eff, max_q, min_q,resolution=15):
        """
        Used in Python based Mosaik simulations as an addition to the qstorage_mosaik.heatstorageSim class.


        ...

        Parameters
        ----------
        soc_init : ???
            ???
        max_temperature : float
            ???
        min_temperature : float
            ???
        insulation : ???
            ???
        ext_temp : float
            ???
        therm_cond : ???
            ???
        length : float
            ???
        diameter : float
            ???
        density : float
            ???
        c : ???
            ???
        eff : ???
            ???
        max_q : ???
            ???
        min_q : ???
            ???
        resolution : ???
            ???

        Attributes
        ----------
        self.flag : int
            ???
        self.q_soc : ???
            ???
        self.max_temperature : float
            ???
        self.min_temperature : float
            ???
        self.insulation : ???
            ???
        self.ext_temp : float
            ???
        self.therm_cond : ???
            ???
        self.area : float
            ??? np.pi*(diameter/2)**2
        self.length : float
            ???
        self.density : float
            ???
        self.c : ???
            ???
        self.eff : ???
            ???
        self.max_q : ???
            ???
        self.min_q : ???
            ???

        self.t_int = (max_temperature - min_temperature) * soc_init / 100 + min_temperature
        self.capacity = (max_temperature - min_temperature) * self.density * self.area * self.length * self.c
        self.q_loss = 0
        self.resolution=resolution #min
        """
        self.flag = 0
        self.q_soc = soc_init
        self.max_temperature = max_temperature
        self.min_temperature = min_temperature
        self.insulation = insulation
        self.ext_temp = ext_temp
        self.therm_cond = therm_cond
        self.area = np.pi*(diameter/2)**2
        self.length = length
        self.density = density
        self.c = c
        self.eff = eff
        self.max_q = max_q
        self.min_q = min_q

        self.t_int = (max_temperature - min_temperature) * soc_init / 100 + min_temperature
        self.capacity = (max_temperature - min_temperature) * self.density * self.area * self.length * self.c
        self.q_loss = 0
        self.resolution=resolution #min

    def charge_q(self, flow2qs:float) -> dict:
        """
        Description (?)
        Returns the parameters `q_flow`, `t_int`, `q_soc`, `mod`, `flag`, `q_loss`

        ...

        Parameters
        ----------
        flow2qs : float
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        q_flow = min(self.max_q, flow2qs)  #kW
        if q_flow > 0:
            qcharge = q_flow * self.eff * self.resolution / 60               # kWh
            t_int = qcharge/(self.density * self.area * self.length * self.c) + self.t_int
            q_capacity = ((self.max_temperature - self.t_int) / self.max_temperature) * self.capacity  # remaining cap
            if self.t_int >= self.max_temperature:
                self.t_int = self.max_temperature
                self.flag = 1
                output_show = 0
            else:
                if qcharge <= q_capacity:
                    self.flag = 0
                    output_show = q_flow / self.eff
                    self.t_int = t_int

                else:  # Fully-charge Case
                    q_consumed = q_capacity / self.eff
                    q_excess = qcharge - q_consumed
                    output_show = q_consumed/(self.resolution/60)
                    self.t_int = self.max_temperature
                    self.flag = 1
        elif q_flow == 0:
            output_show = 0
        self.q_soc =(self.t_int -self.min_temperature)/(self.max_temperature-self.min_temperature) * 100
        self.q_soc = round(self.q_soc, 3)
        re_params = {
                     'q_flow': output_show,
                     't_int': self.t_int,
                     'q_soc': self.q_soc,
                     'mod': 1,
                     'flag': self.flag,
                    'q_loss': self.q_loss}
        return re_params

    def discharge_q(self, flow2qs:float) -> dict:
        """
        Description (?)
        Returns the parameters `q_flow`, `t_int`, `q_soc`, `mod`, `flag`, `q_loss`

        ...

        Parameters
        ----------
        flow2qs : float
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        q_flow = max(self.min_q, flow2qs)
        if q_flow < 0:
            qdischarge = -q_flow / self.eff * self.resolution / 60
            t_int = self.t_int - qdischarge / (self.density * self.area * self.length * self.c)
            q_capacity = ((self.t_int - self.min_temperature) / self.min_temperature) * self.capacity  # remaining cap
            if self.t_int <= self.min_temperature:
                self.t_int = self.min_temperature
                self.flag = -1
                output_show = 0
            else:
                if qdischarge < q_capacity:
                    self.flag = 0
                    output_show = q_flow * self.eff
                    self.t_int = t_int

                else:  # Fully-discharge Case
                    q_given = q_capacity * self.eff
                    q_excess = qdischarge - q_given
                    output_show = q_given/(self.resolution/60)
                    self.t_int = self.min_temperature
                    self.flag = -1
        elif q_flow == 0:
            output_show = 0
        self.q_soc =(self.t_int -self.min_temperature)/(self.max_temperature-self.min_temperature) * 100
        self.q_soc = round(self.q_soc, 3)
        re_params = {
            'q_flow': output_show,
            'q_soc': self.q_soc,
            't_int': self.t_int,
            'mod': -1,
            'flag': self.flag,
            'q_loss': self.q_loss}

        return re_params

    def output_q(self, flow2qs:float) -> dict:
        """
        Description (?)
        Returns the parameters `q_flow`, `t_int`, `q_soc`, `mod`, `flag`, `q_loss`

        ...

        Parameters
        ----------
        flow2qs : float
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        self.q_loss = (self.therm_cond/self.insulation)*self.area*(self.t_int - self.ext_temp)
        flow2qs -= self.q_loss
        if flow2qs == 0:
            if self.t_int >= self.max_temperature:
                self.flag = 1  # meaning battery object is fully charged
            elif self.t_int <= self.min_temperature:
                self.flag = -1  # meaning battery object is fully discharged
            else:
                self.flag = 0  # meaning it is available to operate.
            re_params = {
                         'q_flow': 0,
                         'q_soc': self.q_soc,
                         't_int': self.t_int,
                         'mod': 0,
                         'flag': self.flag,
                         'q_loss': self.q_loss}

        elif flow2qs < 0:  # discharge
            re_params = self.discharge_q(flow2qs)

        else:           # charge
            re_params = self.charge_q(flow2qs)

        return re_params
