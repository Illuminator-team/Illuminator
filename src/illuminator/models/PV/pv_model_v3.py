from illuminator.builder import IlluminatorModel, ModelConstructor
import numpy as np

# construct the model
class PV(ModelConstructor):
    """
    A class to represent a PV model.
    This class provides methods to calculate PV power output based on environmental conditions and panel specifications.

    Attributes
    parameters : dict
        Dictionary containing PV parameters such as module area, NOCT, efficiencies, peak power, tilt angle, and azimuth.
    inputs : dict
        Dictionary containing environmental inputs like irradiance, temperature, solar angles and wind speed.
    outputs : dict
        Dictionary containing calculated outputs like PV generation and irradiance values.
    states : dict
        Dictionary containing the state variables of the PV model.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    __init__(**kwargs)
        Initializes the PV model with the provided parameters.
    step(time, inputs, max_advance=900)
        Simulates one time step of the PV model.
    connect(G_Gh, G_Dh, G_Bn, Ta, hs, FF, Az)
        Processes input parameters and calculates PV output.
    total_irr()
        Calculates total irradiance on tilted surface.
    Temp_effect()
        Calculates temperature-dependent module efficiency.
    output()
        Calculates final PV power or energy output.
    """

    parameters={
        "m_area": 0,  # Module area of the PV panel in m².
        "NOCT": 0,  # Nominal Operating Cell Temperature of the PV panel in °C.
        "m_efficiency_stc": 0,  # Module efficiency under standard test conditions (STC).
        "G_NOCT": 0,  # Nominal Operating Cell Temperature of the PV panel in °C.
        "P_STC": 0,  # Power output of the module under STC (W).
        "peak_power": 0,  # Peak power output of the module (W).
        "m_tilt": 0,
        'm_az': 0,
        'cap': 0,  # installed capacity
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
    states={'pv_gen': 0}
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the PV model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.cap = self._model.parameters.get('cap')
        self.output_type = self._model.parameters.get('output_type')
        self.NOCT = self._model.parameters.get('NOCT')
        self.m_efficiency_stc = self._model.parameters.get('m_efficiency_stc')
        self.G_NOCT = self._model.parameters.get('G_NOCT')
        self.P_STC = self._model.parameters.get('P_STC')
        self.m_tilt = self._model.parameters.get('m_tilt')
        self.m_az = self._model.parameters.get('m_az')
        self.m_area = self._model.parameters.get('m_area')
        self.sim_start = self._model.parameters.get('sim_start')
        self.G_Gh = 0
        self.G_Dh = 0
        self.G_Bn = 0
        self.Ta = 0
        self.hs = 0
        self.FF = 0
        self.Az = 0
        self.sun_az = 0
        self.svf = 0
        self.g_aoi = 0


    def step(self, time: int, inputs:dict=None, max_advance:int=900) -> None:
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time in seconds
            inputs (dict): Dictionary containing input values from other components:
                - G_Gh (float): Global horizontal irradiance [W/m²]
                - G_Dh (float): Diffuse horizontal irradiance [W/m²]
                - G_Bn (float): Direct normal irradiance [W/m²]
                - Ta (float): Ambient temperature [°C]
                - hs (float): Solar height [rad]
                - FF (float): View factor to sky [-]
                - Az (float): Solar azimuth [rad]
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 900.
        Returns:
            float: Next simulation time in seconds
        """
        
        input_data = self.unpack_inputs(inputs)
        self.G_Gh = input_data['G_Gh']
        self.G_Dh = input_data['G_Dh']
        self.G_Bn = input_data['G_Bn']
        self.Ta = input_data['Ta']
        self.hs = input_data['hs']
        self.FF = input_data['FF']
        self.Az = input_data['Az']

        results = self.output()

        self.set_outputs({'pv_gen': results['pv_gen']})

        return time + self._model.time_step_size


    def sun_azimuth(self):  # need to load sun_az
        """
        Getter for the `self.sun_az` attribute

        ...

        Returns
        -------
        sun_azimuth : float
            Sun azimuth angle in degrees, indicating the sun's position in the horizontal plane.
        sun_azimuth : float
            Sun azimuth angle in degrees, indicating the sun's position in the horizontal plane.
        """
        sun_azimuth = self.sun_az
        return sun_azimuth

    def sun_elevation(self):
        """
        Getter for the `self.sun_el` attribute

        ...

        Returns
        -------
        sun_elevation : float
            Solar elevation angle in degrees, indicating the height of the sun in the sky.
        sun_elevation : float
            Solar elevation angle in degrees, indicating the height of the sun in the sky.
        """
        sun_elevation = self.hs
        sun_elevation = self.hs
        return sun_elevation

    def aoi(self):
        """
        Calculates the cosine of the angle of incidence (AOI) between the sun's rays and the PV module surface.

        Takes into account:
        - Module tilt angle
        - Sun elevation angle
        - Sun azimuth angle
        - Module azimuth angle
        Calculates the cosine of the angle of incidence (AOI) between the sun's rays and the PV module surface.

        Takes into account:
        - Module tilt angle
        - Sun elevation angle
        - Sun azimuth angle
        - Module azimuth angle

        Returns
        -------
        cos_aoi : float
            Cosine of the angle of incidence (AOI) as a fraction
            Cosine of the angle of incidence (AOI) as a fraction
        """
        cos_aoi = np.array(np.cos(np.radians(90 - self.m_tilt)) * np.cos(np.radians(self.sun_elevation())) * np.cos(
            np.radians(self.m_az - self.sun_azimuth())) + np.sin(np.radians(90 - self.m_tilt)) * np.sin(
            self.sun_elevation()))
        if cos_aoi < 0:
            cos_aoi = 0
        return cos_aoi

    def diffused_irr(self) -> float:
        """
        Calculates diffuse irradiance on the tilted PV surface.
        Calculates diffuse irradiance on the tilted PV surface.

        Takes into account:
        - Sky view factor (SVF) based on module tilt
        - Diffuse Horizontal Irradiance (DHI)
        Takes into account:
        - Sky view factor (SVF) based on module tilt
        - Diffuse Horizontal Irradiance (DHI)

        Returns
        -------
        g_diff : float
            Diffuse irradiance on the tilted PV surface in W/m²
            Diffuse irradiance on the tilted PV surface in W/m²
        """
        self.svf = np.array((1 + np.cos(np.radians(self.m_tilt))) / 2)
        g_diff = self.svf * self.G_Dh  # global diffused irradiance #W/m2
        self.svf = np.array((1 + np.cos(np.radians(self.m_tilt))) / 2)
        g_diff = self.svf * self.G_Dh  # global diffused irradiance #W/m2
        return g_diff

    def reflected_irr(self) -> float:
        """
        Calculates ground-reflected irradiance on the PV module.
        Calculates ground-reflected irradiance on the PV module.

        Takes into account:
        - Albedo (reflectivity) of the ground surface
        - Sky view factor (SVF) based on module tilt
        - Global Horizontal Irradiance (GHI)
        Takes into account:
        - Albedo (reflectivity) of the ground surface
        - Sky view factor (SVF) based on module tilt
        - Global Horizontal Irradiance (GHI)

        Returns
        -------
        g_ref : float
            Ground-reflected irradiance on the PV module in W/m²
            Ground-reflected irradiance on the PV module in W/m²
        """
        albedo = 0.2
        g_ref = albedo * (1 - self.svf) * self.G_Gh
        g_ref = albedo * (1 - self.svf) * self.G_Gh
        return g_ref

    def direct_irr(self) -> float:
        """
        Calculates direct beam irradiance on tilted surface.
        Calculates direct beam irradiance on tilted surface.

        Accounts for angle of incidence between sun rays and module surface.
        Accounts for angle of incidence between sun rays and module surface.

        Returns
        -------
        g_dir : float
            Direct beam irradiance on tilted surface in W/m²
            Direct beam irradiance on tilted surface in W/m²
        """
        g_dir = self.G_Bn * self.aoi()
        g_dir = self.G_Bn * self.aoi()
        return g_dir

    def total_irr(self) -> float:
        """
        Calculates total irradiance on the tilted PV surface.
        Calculates total irradiance on the tilted PV surface.

        Combines direct beam, diffuse, and ground-reflected irradiance components
        accounting for module tilt and orientation.
        Combines direct beam, diffuse, and ground-reflected irradiance components
        accounting for module tilt and orientation.

        Returns
        -------
        self.g_aoi : float
            Total irradiance on tilted surface in W/m²
            Total irradiance on tilted surface in W/m²
        """
        self.g_aoi = self.diffused_irr() + self.reflected_irr() + self.direct_irr()
        return self.g_aoi


    # the effect of temperature and wind speed on the module efficiency.
    def Temp_effect(self) -> float:
        """
        Calculates the temperature-dependent module efficiency.
        Calculates the temperature-dependent module efficiency.

        Takes into account:
        - Module temperature based on NOCT conditions
        - Wind speed effects
        - Temperature coefficient of efficiency
        Takes into account:
        - Module temperature based on NOCT conditions
        - Wind speed effects
        - Temperature coefficient of efficiency

        Returns
        -------
        efficiency : float
            Temperature-adjusted module efficiency as a fraction
            Temperature-adjusted module efficiency as a fraction
        """
        m_temp = self.Ta + (np.divide(self.total_irr(), self.G_NOCT)) * (self.NOCT - 20) * (
            np.divide(9.5, (5.7 + 3.8 * self.FF))) * (1 - (self.m_efficiency_stc / 0.90))
        m_temp = self.Ta + (np.divide(self.total_irr(), self.G_NOCT)) * (self.NOCT - 20) * (
            np.divide(9.5, (5.7 + 3.8 * self.FF))) * (1 - (self.m_efficiency_stc / 0.90))

        efficiency = self.m_efficiency_stc * (1 + (-0.0035 * (m_temp - 25)))
        return efficiency

    def output(self) -> dict:
        """
        Calculates PV power or energy output based on environmental conditions.
        
        Takes into account:
        - Module temperature effects
        - Inverter and MPPT efficiency
        - System losses
        - Total module area
        - Solar irradiance
        Calculates PV power or energy output based on environmental conditions.
        
        Takes into account:
        - Module temperature effects
        - Inverter and MPPT efficiency
        - System losses
        - Total module area
        - Solar irradiance

        Returns
        -------
        dict
            Dictionary containing:
            - 'pv_gen': PV generation in kW (power) or kWh (energy)
            - 'total_irr': Total irradiance on tilted surface in W/m² <- check
            Dictionary containing:
            - 'pv_gen': PV generation in kW (power) or kWh (energy)
            - 'total_irr': Total irradiance on tilted surface in W/m² <- check
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
        p_ac = 0
        p_ac = 0
        if self.output_type == 'energy':
            p_ac = (total_m_area * self.total_irr() *
                    self.Temp_effect() * inv_eff * mppt_eff * losses)/4 / 1000 # kWh TODO: implement time interval or smh
        elif self.output_type == 'power':
            p_ac = ((total_m_area * self.total_irr() *
                    self.Temp_effect() * inv_eff * mppt_eff * losses) ) / 1000  # kW

        return {'pv_gen': p_ac, 'total_irr': self.g_aoi}