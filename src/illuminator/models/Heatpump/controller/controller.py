import jsonpickle

class Controller():

    def __init__(self, params:dict) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the controller_mosaik.ControllerSimulator class.


        ...

        Parameters
        ----------
        params : dict
            ???

        Attributes
        ----------
        self.T_amb : ???
            ???
        self.heat_source_T : ???
            ???
        self.sh_demand : ???
            ???
        self.sh_supply : ???
            ???
        self.dhw_demand : ???
            ???
        self.dhw_supply : ???
            ???
        self.hp_demand : ???
            ???
        self.hp_supply : ???
            ???
        self.heat_demand : ???
            ???
        self.heat_supply : ???
            ???
        self.hwt_connections : ???
            ???
        self.T_mean : ???
            ???

        self.sh_in_F : ???
            ???
        self.sh_in_T : ???
            ???
        self.sh_out_F : ???
            ???

        self.dhw_in_F : ???
            ???
        self.dhw_in_T : ???
            ???
        self.dhw_out_F : ???
            ???

        self.hp_in_F : ???
            ???
        self.hp_in_T : ???
            ???
        self.hp_out_F : ???
            ???
        self.hp_out_T : ???
            ???
        self.hp_cond_m : ???
            ???
        self.hp_on_fraction : ???
            ???

        self.hwt_mass : ???
            ???

        self.hwt_hr_P_th_set : ???
            ???

        self.hp_signal : ???
            ???
        self.heater_signal : ???
            ???
        self.hp_status : ???
            ???

        self.T_hp_sp_h : ???
            ???
        self.T_hp_sp_l : ???
            ???
        self.T_hr_sp : ???
            ???
        self.T_max : ???
            ???
        self.T_min : ???
            ???
        self.dhw_in_T : ???
            ???
        self.sh_dT : ???
            ???


        self.i : int
            ???
        """
        self.T_amb = None
        self.heat_source_T = None
        self.sh_demand = None
        self.sh_supply = None
        self.dhw_demand = None
        self.dhw_supply = None
        self.hp_demand = None
        self.hp_supply = None
        self.heat_demand = None
        self.heat_supply = None
        self.hwt_connections = None
        self.T_mean = None

        self.sh_in_F = None
        self.sh_in_T = None
        self.sh_out_F = None

        self.dhw_in_F = None
        self.dhw_in_T = None
        self.dhw_out_F = None

        self.hp_in_F = None
        self.hp_in_T = None
        self.hp_out_F = None
        self.hp_out_T = None
        self.hp_cond_m = None
        self.hp_on_fraction = None

        self.hwt_mass = None

        self.hwt_hr_P_th_set = None

        self.hp_signal = None
        self.heater_signal = None
        self.hp_status = None

        self.T_hp_sp_h = params.get('T_hp_sp_h')
        self.T_hp_sp_l = params.get('T_hp_sp_l')
        self.T_hr_sp = params.get('T_hr_sp')
        self.T_max = params.get('T_max')
        self.T_min = params.get('T_min')
        self.dhw_in_T = params.get('dhw_in_T')
        self.sh_dT = params.get('sh_dT')


        self.i = 0

    def step(self) -> None:
        """
        Description
        """

        if self.heat_demand is None or self.heat_demand < 0:
            self.heat_demand = 0
        if self.sh_demand is None or self.sh_demand < 0:
            self.sh_demand = 0
        else:
            self.sh_demand *= 1000
        if self.dhw_demand is None or self.dhw_demand < 0:
            self.dhw_demand = 0

        # self.sh_demand = self.heat_demand/2
        # self.dhw_demand = self.heat_demand/2

        if self.hwt_connections is not None:
            hwt_connections = jsonpickle.decode((self.hwt_connections))

        # self.T_mean = hwt.T_mean

        # sh_fraction, dhw_m_flow = self.calc_dhw_supply(self.step_size, hwt_connections)
        # self.dhw_out_F = - dhw_m_flow
        # self.dhw_in_F = dhw_m_flow
        # self.dhw_in_T = self.dhw_in_T
        
        sh_fraction = 1 

        sh_m_flow, sh_in_T = self.calc_sh_supply(self.step_size, hwt_connections, sh_fraction)
        self.sh_in_F = sh_m_flow
        self.sh_in_T = sh_in_T
        self.sh_out_F = - sh_m_flow

        if self.sh_supply is None:
            self.sh_supply = 0
        if self.dhw_supply is None:
            self.dhw_supply = 0

        self.heat_supply = self.sh_supply + self.dhw_supply

        if self.T_mean < self.T_hp_sp_l:
            self.hp_status = 'on'
            
        if self.hp_status == 'on':
            if self.T_mean < (self.T_hp_sp_h-1):
                self.hp_demand = self.hwt_mass * 4184 * (self.T_hp_sp_h - self.T_mean) / self.step_size
            else:
                self.hp_demand = 0
                self.hp_status = 'off'
        else:
            self.hp_demand = 0

        self.get_hp_out_T(hwt_connections)

        if self.hp_in_T is None:
            self.hp_in_T = self.hp_out_T
        
        if self.hp_supply is None:
            #print('hp_supply is None')
            self.hp_supply = 0

        self.hp_in_F = self.hp_on_fraction * self.hp_cond_m
        self.hp_out_F = -self.hp_on_fraction * self.hp_cond_m
            
        if self.T_hr_sp is not None:
            if self.T_mean < self.T_hr_sp:
                self.hwt_hr_P_th_set = (self.hwt_mass * 4184 * (self.T_hr_sp - self.T_mean)) / self.step_size
            else:
                self.hwt_hr_P_th_set = 0

    def calc_dhw_supply(self, step_size, hwt_connections) -> tuple[float, float]:
        """
        Description

        ...

        Parameters
        ----------
        step_size : ???
            ???
        hwt_connections : ???
            ???
        
        Returns
        -------
        sh_fraction : float
            ???
        dhw_m_flow : float
            ???
        """

        sh_fraction = 1 # remove later

        for key, connection in hwt_connections.items():

            if connection.type == 'dhw_out':
                if connection.T > self.T_min:
                    dhw_m_flow = self.dhw_demand / (4184 * (connection.T - self.dhw_in_T))
                    if dhw_m_flow > (connection.corresponding_layer.volume / step_size):
                        dhw_m_flow = connection.corresponding_layer.volume / step_size
                        sh_fraction = 0
                    else:
                        sh_fraction = (connection.corresponding_layer.volume - (dhw_m_flow * step_size))/connection.corresponding_layer.volume
                else:
                    dhw_m_flow = 0
                    sh_fraction = 1

                self.dhw_supply = dhw_m_flow * 4184 * (connection.T - self.dhw_in_T)

                return sh_fraction, dhw_m_flow

    def calc_sh_supply(self, step_size,  hwt_connections, sh_fraction) -> tuple[float, float]:
        """
        Description

        ...

        Parameters
        ----------
        step_size : ???
            ???
        hwt_connections : ???
            ???
        sh_fraction : ???
            ???
        
        Returns
        -------
        sh_m_flow : float
            ???
        sh_in_T : float
            ???
        """

        for key, connection in hwt_connections.items():

            if connection.type == 'sh_out':
                if self.T_min <= connection.T <= self.T_max:
                    sh_m_flow = self.sh_demand/(4184 * self.sh_dT)
                    if sh_fraction == 0:
                        sh_m_flow = 0
                    elif sh_m_flow > (sh_fraction * connection.corresponding_layer.volume / step_size):
                        sh_m_flow = sh_fraction * connection.corresponding_layer.volume / step_size
                else:
                    sh_m_flow = 0

                self.sh_supply = sh_m_flow * 4184 * self.sh_dT

                # print(connection.T, self.sh_dT)

                sh_in_T = connection.T - self.sh_dT

                return sh_m_flow, sh_in_T

    def get_hp_out_T (self, hwt_connections) -> None:
        """
        Set the `self.hp_out_T` variable based on the `hwt_connections` parameter
        and if the connection is of type `hp_out`

        ...

        Parameters
        ----------
        hwt_connections : ???
            ???   
        """

        for key, connection in hwt_connections.items():

            if connection.type == 'hp_out':
                self.hp_out_T = connection.T
