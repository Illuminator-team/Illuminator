import numpy as np
from numpy import sin, cos

class PV_py_model:

    def __init__(self, panel_data, m_tilt, m_az, cap, output_type) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the gpcontroller_mosaik.gpcontrolSim class.
        
        ...

        Parameters
        ----------
        panel_data : ???
            ???
        m_tilt : ???
            ???
        m_az : ???
            ???
        cap : ???
            ???
        output_type : ???
            ???

        Attributes
        ----------
        self.m_area : ???
            Module area. Available in the spec sheet of a pv module
        self.NOCT : float
            Expressed in degree celsius
        self.m_efficiency_stc : ???
            ???
        self.G_NOCT : ???
            Expressed in W/m2. 
            This is the irradiance that falls on the panel under NOCT conditions
        self.P_STC : ???
            Expressed in Watts. Available in spec sheet of a module.
        self.m_tilt : ???
            ???
        self.m_az : ???
            ???
        self.cap : ???
            ???
        self.output_type : ???
            ???
        """
        # with open ('L1234.csv') as data:
        #     self.start_date=data.readline(1)
        # self.start_date = (genfromtxt('L1234.csv', delimiter=',', usecols=0, max_rows=1, skip_header=1))
        # self.temp = None
        # self.dhi = None
        # self.ghi = None
        # self.dni = None
        # self.ws = None
        # self.sun_el = None
        # self.sun_az = None
        self.m_area = panel_data['Module_area']
        # module area. available in the spec sheet of a pv module
        self.NOCT = panel_data['NOCT']  #degree celsius
        self.m_efficiency_stc = panel_data['Module_Efficiency']
        self.G_NOCT = panel_data['Irradiance_at_NOCT']
        # W/m2 This is the irradiance that falls on the panel under NOCT conditions
        self.P_STC = panel_data['Power_output_at_STC']
        # Watts. Available in spec sheet of a module
        self.m_tilt = m_tilt
        self.m_az = m_az
        self.cap = cap
        self.output_type = output_type

    def sun_azimuth(self):  # need to load sun_az
        """
        Getter for the `self.sun_az` attribute

        ...

        Returns
        -------
        sun_azimuth : ???
            ???
        """
        sun_azimuth = self.sun_az
        return sun_azimuth

    def sun_elevation(self):
        """
        Getter for the `self.sun_el` attribute

        ...

        Returns
        -------
        sun_elevation : ???
            ???
        """
        sun_elevation = self.sun_el
        return sun_elevation

    def aoi(self):
        """
        Description
        
        ...

        Returns
        -------
        cos_aoi : ???
            ???
        """
        cos_aoi = np.array(cos(np.radians(90 - self.m_tilt)) * cos(np.radians(self.sun_elevation())) * cos(
            np.radians(self.m_az - self.sun_azimuth())) + sin(np.radians(90 - self.m_tilt)) * sin(
            self.sun_elevation()))
        if cos_aoi < 0:
            cos_aoi = 0
        return cos_aoi

    def diffused_irr(self) -> float:
        """
        Description

        ...

        Returns
        -------
        g_diff : float
            ???
        """
        self.svf = np.array((1 + cos(np.radians(self.m_tilt))) / 2)
        g_diff = self.svf * self.dhi  # global diffused irradiance #W/m2
        return g_diff

    def reflected_irr(self) -> float:
        """
        Description

        ...

        Returns
        -------
        g_ref : float
            ???
        """
        albedo = 0.2
        g_ref = albedo * (1 - self.svf) * self.ghi
        return g_ref

    def direct_irr(self) -> float:
        """
        Description

        ...

        Returns
        -------
        g_dir : float
            ???
        """
        g_dir = self.dni * self.aoi()
        return g_dir

    def total_irr(self) -> float:
        """
        Description

        ...

        Returns
        -------
        self.g_aoi : float
            ???
        """
        self.g_aoi = self.diffused_irr() + self.reflected_irr() + self.direct_irr()
        return self.g_aoi


    # the effect of temperature and wind speed on the module efficiency.
    def Temp_effect(self) -> float:
        """
        Description

        ...

        Returns
        -------
        efficiency : float
            ???
        """
        m_temp = self.temp + (np.divide(self.total_irr(), self.G_NOCT)) * (self.NOCT - 20) * (
            np.divide(9.5, (5.7 + 3.8 * self.ws))) * (1 - (self.m_efficiency_stc / 0.90))

        efficiency = self.m_efficiency_stc * (1 + (-0.0035 * (m_temp - 25)))
        return efficiency

    def output(self) -> dict:
        """
        Description

        ...

        Returns
        -------
        dict
            Collection of parameters and their respective values
        """

        # constants
        # inverter efficiency. We can use sandia model to actually find an inverter that suits our needs
        inv_eff = 0.96
        mppt_eff = 0.99  # again, can calculate it accurately
        losses = 0.97  # other losses
        sf = 1.1

        # generation calculation
        num_of_modules = np.ceil(self.cap * sf / self.P_STC)


        # [W] again we get this for every time step
        # this is for the DC output from the number of panes we require (calculated above) at every hour
        p_dc = self.Temp_effect() * num_of_modules * self.m_area * self.total_irr()
        total_m_area = num_of_modules * self.m_area

        # AC output at every hour from all the panels (a solar farm)

        if self.output_type == 'energy':
            p_ac = (total_m_area * self.total_irr() *
                    self.Temp_effect() * inv_eff * mppt_eff * losses)/4  # kWh
        elif self.output_type == 'power':
            p_ac = ((total_m_area * self.total_irr() *
                    self.Temp_effect() * inv_eff * mppt_eff * losses) )  # kW

        return {'pv_gen': p_ac, 'total_irr': self.g_aoi}

    def connect(self, G_Gh, G_Dh, G_Bn, Ta, hs, FF, Az) -> dict:
        """
        Sets class attributes and runs the `self.output()` function, returning its output.

        Paramter
        --------
        G_Gh : ???
            ???
        G_Dh : ???
            ???
        G_Bn, : ???
            ???
        Ta : ???
            ???
        hs : ???
            ???
        FF : ???
            ???
        Az : ???
            ???

        Returns
        -------
        dict 
            Collection of parameters and their respective values
        """
        self.ghi = G_Gh
        self.dhi = G_Dh
        self.dni = G_Bn
        self.temp = Ta
        self.sun_el = hs
        self.ws = FF
        self.sun_az = Az
        # print( self.sun_az, self.ws, self.dni)
        # print('1')
        # print(sun_az, ws, dni, dhi, ghi, sun_el, ambient_temp)
        return self.output()

