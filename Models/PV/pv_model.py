import numpy as np
from numpy import sin, cos

class PV_py_model:

    def __init__(self, panel_data, m_tilt, m_az, cap, output_type='power', resolution=15):
        self.m_area = panel_data['Module_area']
        # module area. available in the spec sheet of a pv module
        self.NOCT = panel_data['NOCT']  #degree celsius
        self.m_efficiency_stc = panel_data['Module_Efficiency']
        self.G_NOCT = panel_data['Irradiance_at_NOCT']
        # W/m2 This is the irradiance that falls on the panel under NOCT conditions
        self.P_STC = panel_data['Power_output_at_STC']
        # Watts. Available in spec sheet of a module
        self.peak_power=panel_data['peak_power']
        self.m_tilt = m_tilt
        self.m_az = m_az
        self.cap = cap
        self.output_type = output_type
        self.resolution = resolution
        self.time_interval = self.resolution / 60

    def sun_azimuth(self):  # need to load sun_az
        sun_azimuth = self.sun_az
        return sun_azimuth

    def sun_elevation(self):
        sun_elevation = self.sun_el
        return sun_elevation

    def aoi(self):
        cos_aoi = np.array(cos(np.radians(90 - self.m_tilt)) * cos(np.radians(self.sun_elevation())) * cos(
            np.radians(self.m_az - self.sun_azimuth())) + sin(np.radians(90 - self.m_tilt)) * sin(
            self.sun_elevation()))
        if cos_aoi < 0:
            cos_aoi = 0
        return cos_aoi

    def diffused_irr(self):
        self.svf = np.array((1 + cos(np.radians(self.m_tilt))) / 2)
        g_diff = self.svf * self.dhi  # global diffused irradiance #W/m2
        return g_diff

    def reflected_irr(self):
        albedo = 0.2
        g_ref = albedo * (1 - self.svf) * self.ghi
        return g_ref

    def direct_irr(self):
        g_dir = self.dni * self.aoi()
        return g_dir

    def total_irr(self):
        self.g_aoi = self.diffused_irr() + self.reflected_irr() + self.direct_irr()
        return self.g_aoi


    # the effect of temperature and wind speed on the module efficiency.
    def Temp_effect(self):
        m_temp = self.temp + (np.divide(self.total_irr(), self.G_NOCT)) * (self.NOCT - 20) * (
            np.divide(9.5, (5.7 + 3.8 * self.ws))) * (1 - (self.m_efficiency_stc / 0.90))

        efficiency = self.m_efficiency_stc * (1 + (-0.0035 * (m_temp - 25)))
        return efficiency

    def output(self):

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
        #p_dc = self.Temp_effect() * num_of_modules * self.m_area * self.total_irr()
        total_m_area = num_of_modules * self.m_area

        # AC output at every hour from all the panels (a solar farm)

        if self.output_type == 'energy':
            p_ac = (total_m_area * self.total_irr() *
                    self.Temp_effect() * inv_eff * mppt_eff * losses)/4  # kWh
        elif self.output_type == 'power':
            p_ac = ((total_m_area * self.total_irr() *
                    self.Temp_effect() * inv_eff * mppt_eff * losses) )  # kW

        return {'pv_gen': p_ac, 'total_irr': self.g_aoi}

    def connect(self, G_Gh, G_Dh, G_Bn, Ta, hs, FF, Az):
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

