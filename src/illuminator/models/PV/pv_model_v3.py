from illuminator.builder import IlluminatorModel, ModelConstructor

# Define the model parameters, inputs, outputs...
pv = IlluminatorModel(
    parameters={
        "m_area": 0,  # Module area of the PV panel in m².
        "NOCT": 0,  # Nominal Operating Cell Temperature of the PV panel in °C.
        "m_efficiency_stc": 0,  # Module efficiency under standard test conditions (STC).
        "G_NOCT": 0,  # Nominal Operating Cell Temperature of the PV panel in °C.
        "P_STC": 0,  # Power output of the module under STC (W).
        "peak_power": 0,  # Peak power output of the module (W).
        "time_interval": 0  # Time interval for the simulation in hours, derived from the resolution parameter.
        },
    inputs={
        "G_Gh": 0,  # Global Horizontal Irradiance (GHI) in W/m², representing the total solar radiation received on a horizontal surface.
        "G_Dh": 0,  # Diffuse Horizontal Irradiance (DHI) in W/m², representing the solar radiation received from the sky, excluding the solar disk.
        "G_Bn": 0,  # Direct Normal Irradiance (DNI) in W/m², representing the solar radiation received directly from the sun on a surface perpendicular to the sun’s rays.
        "Ta": 0,  # Ambient temperature (°C) of the environment surrounding the PV panels.
        "hs": 0,  # Solar elevation angle (degrees), indicating the height of the sun in the sky.
        "FF": 0,  # Wind speed (m/s), which affects the temperature and performance of the PV panels.
        "Az": 0  # Sun azimuth angle (degrees), indicating the sun's position in the horizontal plane.
        },
    outputs={
        "pv_gen": 0,  # Generated PV power output (kW) or energy (kWh) based on the chosen output type (power or energy).
        "total_irr": 0,  # Total irradiance (W/m²) received on the PV module, considering direct, diffuse, and reflected components.
        "g_aoi": 0  # Total irradiance (W/m²) accounting for angle of incidence, diffuse, and reflected irradiance.
        },
    states={
        "g_aoi": 0  # Total irradiance (W/m²) accounting for angle of incidence, diffuse, and reflected irradiance.
        },
    time_step_size=1,
    time=None
    )

# construct the model
class PV(ModelConstructor):
    parameters={
        "m_area": 0,  # Module area of the PV panel in m².
        "NOCT": 0,  # Nominal Operating Cell Temperature of the PV panel in °C.
        "m_efficiency_stc": 0,  # Module efficiency under standard test conditions (STC).
        "G_NOCT": 0,  # Nominal Operating Cell Temperature of the PV panel in °C.
        "P_STC": 0,  # Power output of the module under STC (W).
        "peak_power": 0,  # Peak power output of the module (W).
        "m_tilt": 0,
        'm_az': 0,
        'cap': 0,
        'output_type': 'power',
        'sim_start': 0
        }
    inputs={
        "G_Gh": 0,  # Global Horizontal Irradiance (GHI) in W/m², representing the total solar radiation received on a horizontal surface.
        "G_Dh": 0,  # Diffuse Horizontal Irradiance (DHI) in W/m², representing the solar radiation received from the sky, excluding the solar disk.
        "G_Bn": 0,  # Direct Normal Irradiance (DNI) in W/m², representing the solar radiation received directly from the sun on a surface perpendicular to the sun’s rays.
        "Ta": 0,  # Ambient temperature (°C) of the environment surrounding the PV panels.
        "hs": 0,  # Solar elevation angle (degrees), indicating the height of the sun in the sky.
        "FF": 0,  # Wind speed (m/s), which affects the temperature and performance of the PV panels.
        "Az": 0  # Sun azimuth angle (degrees), indicating the sun's position in the horizontal plane.
        }
    outputs={
        "pv_gen": 0,  # Generated PV power output (kW) or energy (kWh) based on the chosen output type (power or energy).
        "total_irr": 0,  # Total irradiance (W/m²) received on the PV module, considering direct, diffuse, and reflected components.
        "g_aoi": 0  # Total irradiance (W/m²) accounting for angle of incidence, diffuse, and reflected irradiance.
        }
    states={}
    time_step_size=1
    time=None

    def step(self, time, inputs, max_advance=900) -> None:
        for eid, attrs in inputs.items():

            v = []  # we create this empty list to hold all the input values we want to give since we have more than 2
            for attr, vals in attrs.items():

                # inputs is a dictionary, which contains another dictionary.
                # value of U is a list. we need to combine all the values into a single list. But is we just simply
                #   append them in v, we have a nested list, hence just 1 list. that creates a problem as it just
                #   gives all 7 values to only sun_az in the python model and we get an error that other 6 values are missing.
                u = list(vals.values())
                v.append(u)  # we append every value of u to v from this command.

            # the following code helps us to convert the nested list into a simple plain list and we can use that simply
            v_merged = list(itertools.chain(*v))

            self._cache[eid] = self.connect(v_merged[0], v_merged[1], v_merged[2], v_merged[3],
                                                          v_merged[4], v_merged[5], v_merged[6]) # PV1
        return time + self._model.time_step_size


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
        cos_aoi : float
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

if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    pv_model = PV(pv)

    print(pv_model.step(1))