# compressed hydrogen storage tank at 700bar and storing about 100kg of hydrogen

class hydrogenstorage_python:
    def __init__(self, initial_set:dict, h2_set:dict) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the h2storage_mosaik.compressedhydrogen class.

        ...

        Parameters
        ----------
        initial_set : ???
            ???
        h2_set : ???
            ???

        Attributes
        ----------
        self.h2storage_soc : int
            ???
        self.h2storage_soc_min : int
            ???
        self.h2storage_soc_max : int
            ???
        self.eff : float
            ???
        self.max_h2 : float
            ???
        self.min_h2 : float
            ???
        self.capacity : int
            ???
        self.resolution : int
            ???
        self.flag : int
            ???
        self.output_show : int
            ???
        self.output2_show : int
            ???
        """
        self.h2storage_soc = initial_set['initial_soc']
        self.h2storage_soc_min = h2_set['h2storage_soc_min']
        self.h2storage_soc_max = h2_set['h2storage_soc_max']
        self.eff = h2_set['eff']
        self.max_h2 = h2_set['max_h2']
        self.min_h2 = h2_set['min_h2']
        self.capacity = h2_set['capacity']
        self.resolution=h2_set['resolution']
        self.flag = 0
        self.output_show=0
        self.output2_show=0

    def charge_h2(self, flow2h2s_net) -> dict:
        """
        Description (?)

        ...

        Parameters
        ----------
        flow2h2s_net : ???
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values.
        """
        h2_flow = min(self.max_h2, flow2h2s_net)  # m^3/min
        if h2_flow > 0:
            h2discharge = h2_flow * self.eff * self.resolution                # m^3
            h2_capacity = ((self.h2storage_soc_max - self.h2storage_soc) / 100) * self.capacity
            if self.h2storage_soc >= self.h2storage_soc_max:
                self.flag = 1
                self.output_show = 0
            else:
                if h2discharge <= h2_capacity:
                    self.h2storage_soc = self.h2storage_soc + (h2discharge / self.capacity * 100)
                    self.flag = 0
                    self.output_show = h2_flow

                else:  # Fully-charge Case
                    h2_consumed = h2_capacity / self.eff
                    h2_excess = h2discharge - h2_consumed
                    self.output2_show = h2_excess / self.resolution
                    self.output_show = h2_consumed/self.resolution                #m^3/min
                    self.h2storage_soc = self.h2storage_soc_max
                    self.flag = 1
        elif h2_flow == 0:
            self.output_show = 0
        self.h2storage_soc = round(self.h2storage_soc, 3)
        re_params = {'h2_flow': self.output_show,
                     'h2_excess_flow': self.output2_show,
                     'h2_soc': self.h2storage_soc,
                     'mod': 1,
                     'flag': self.flag}
        return re_params

    def discharge_h2(self, flow2h2s_net) -> dict:
        """
        Description (?)

        ...

        Parameters
        ----------
        flow2h2s_net : ???
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values.
        """
        h2_flow = max(self.min_h2, flow2h2s_net)   # m^3/min
        if h2_flow < 0:
            h2discharge = h2_flow / self.eff * self.resolution               # m^3
            h2_capacity = ((self.h2storage_soc_min - self.h2storage_soc) / 100) * self.capacity
            if self.h2storage_soc <= self.h2storage_soc_min:
                self.flag = -1
                self.output_show = 0
            else:
                if h2discharge > h2_capacity:
                    h2_given = h2discharge
                    self.h2storage_soc = self.h2storage_soc + (h2discharge / self.capacity * 100)
                    self.flag = 0
                    self.output_show = h2_flow

                else:  # Fully-discharge Case
                    h2_given = h2_capacity * self.eff
                    h2_excess = h2discharge - h2_given
                    self.output2_show=h2_excess/self.resolution
                    self.output_show = h2_given/self.resolution               #m^3/min
                    self.h2storage_soc = self.h2storage_soc_min
                    self.flag = -1
        else:
            self.output_show = 0
        self.h2storage_soc = round(self.h2storage_soc, 3)
        re_params = {
            'h2_flow': self.output_show,
            'h2_excess_flow':self.output2_show,
            'h2_soc': self.h2storage_soc,
            'mod': 1,
            'flag': self.flag}

        return re_params

    def output_h2(self, flow2h2s:int, eleh2_in:int, fuelh2_out:float, soc:int) -> dict:
        """
        Description (?)

        ...

        Parameters
        ----------
        flow2h2s : int
            ???
        eleh2_in : int
            ???
        fuelh2_out : float
            ???
        soc : int
            The current state of charge (SOC)

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values.
        """
        self.h2storage_soc = soc
        flow2h2s_net=flow2h2s+eleh2_in-fuelh2_out
        if flow2h2s_net == 0:  # i.e when there isn't a demand of hydrogen at all,
            if self.h2storage_soc >= self.h2storage_soc_max:
                self.flag = 1  # meaning battery object is fully charged
            elif self.h2storage_soc <= self.h2storage_soc_min:
                self.flag = -1  # meaning battery object is fully discharged
            else:
                self.flag = 0  # meaning it is available to operate.
            re_params = {'flow2h2s': flow2h2s,
                         'eleh2_in': eleh2_in,
                         'fuelh2_out': fuelh2_out,
                         'h2_flow': 0,
                         'h2_excess_flow': 0,
                         'h2_soc': self.h2storage_soc,
                         'mod': 0,
                         'flag': self.flag}

        elif flow2h2s_net < 0:  # discharge
            re_params={'flow2h2s': flow2h2s,
                         'eleh2_in': eleh2_in,
                         'fuelh2_out': fuelh2_out}
            re_params.update(self.discharge_h2(flow2h2s_net))

        else:           # charge
            re_params = {'flow2h2s': flow2h2s,
                           'eleh2_in': eleh2_in,
                           'fuelh2_out': fuelh2_out}
            re_params.update(self.charge_h2(flow2h2s_net))

        return re_params
