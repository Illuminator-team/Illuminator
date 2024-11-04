# -*- coding: utf-8 -*-

from datetime import datetime

"""
The hotwatertank module contains classes for the components of the hotwatertank
(:class:`Layer`, :class:`Connection`, :class:`Sensor`, :class:`HeatingRod`) 
and a class for the hotwater tank itself (:class:`HotWaterTank`).

"""
import jsonpickle
import numpy as np

C_W = 4180  # specific heat capacity of water in J/(kgK)
RHO = 1  # density of water [kg/l]

# class HotWaterTank(object):
class HotWaterTank():
    """
    Simulation model of a hotwater tank.

    Stratification is modelled by a number of :class:`Layer` objects. Heat
    producers and consumers can be connected to the hotwatertank via
    :class:`Connection` objects. The temperature at different positions in the
    tank can be accessed via :class:`Sensor` objects.

    Hotwater tank parameters are provided at instantiation by the dictionary
    **params**. This is an example, how the dictionary might look like::

        params = {
            'height': 2100,
            'diameter': 1200,
            'T_env': 20.0,
            'htc_walls': 1.0,
            'htc_layers': 20,
            'n_layers': 3,
            'n_sensors': 3,
            'connections': {
                'cc_in': {'pos': 0},
                'cc_out': {'pos': 2099},
                'gcb_in': {'pos': 1700},
                'gcb_out': {'pos': 500}
                },
            'heating_rods': {
                'hr_1': {
                    'pos': 1800,
                    'P_th_stages': [0, 500, 1000, 2000, 3000]
                    }
                }
            }

    Explanation of the entries in the dictionary:

    * **height**: height of the tank in mm
    * **diameter**: diameter of the tank in mm
    * **volume**: alternatively to the diameter the volume of the tank in liter
      can be specified
    * **T_env**: ambient temperature in °C
    * **htc**: heat transfer coefficient of tank walls in W/(m2K)
    * **htc_layers**: imaginary heat transfer coefficient between layers in
      W/(m2K)
    * **n_layers**: number of layers, n layers of the same dimension are
      created
    * **n_sensors**: number of sensors, the sensors are equidistantly
      distributed in the hotwater tank, sensors are named 'sensor_00',
      'sensor_01', ..., 'sensor_n-1' with 'sensor_00' indexing the undermost
      sensor
    * **connections**: each connection is specified by an dictionary with a
      structure analog to the example
    * **heating_rods**: each heating rod is specified by an dictionary with a
      structure analog to the example

    It is also possible to define layers and sensors explicitly::

        params = {
            'height': 2100,
            'diameter': 1200,
            'T_env': 20.0,
            'htc_walls': 1.0,
            'htc_layers': 20,
            'layers': [
                {'bottom': 0, 'top': 500},
                {'bottom': 500, 'top': 1600},
                {'bottom': 1600, 'top': 2100}
                ],
            'sensors': {
                'sensor_1', {'pos': 200},
                'sensor_2', {'pos': 1900},
                },
            'connections': {
                'cc_in': {'pos': 0},
                'cc_out': {'pos': 2099},
                'gcb_in': {'pos': 1700},
                'gcb_out': {'pos': 500}
                },
            'heating_rods': {
                'hr_1': {
                    'pos': 1800,
                    'P_th_stages': [0, 500, 1000, 2000, 3000]
                    }
                }
            }

    Initial values for the temperature distribution in the tank  or the
    initial el. power of the heating rod are provided by the
    dictionary init_vals, which might look like this::

        {
            'layers': {'T': 50},
            'hr_1': { 'P_el': 2000}
        }

    this::

        {
            'layers': {'T': [30, 50, 70]}
            'hr_1': { 'P_el': 2000}
        }

    or this::

        {
            'layers': {'T': [30, 70]},
            'hr_1': { 'P_el': 2000}
        }


    * **T**: initial temperature of tank in °C, alternatively a
      temperature range can be specified, whereby the lower limit defines the
      temperature of ther undermost layer and the upper limit the temperature
      of the uppermost layer, inbetween a linear temperature gradient is set,
      it is also possible to specify the temperature of each layer individually
      by passing a list of length n_layers

    **Example**

    .. literalinclude:: ../pysimmods/hotwatertanksim/example.py

    """

    def __init__(self, params:dict, init_vals:dict=None) -> None:
        """
        Simulation model of a hotwater tank.
        Used in Python based Mosaik simulations as an addition to the hotwatertank_mosaik.HotWaterTankSimulator class.


        Parameters
        ----------
        params : dict
            Hotwater tank parameters. 
            An example of how the dictionary might look like::

                params = {
                    'height': 2100,
                    'diameter': 1200,
                    'T_env': 20.0,
                    'htc_walls': 1.0,
                    'htc_layers': 20,
                    'n_layers': 3,
                    'n_sensors': 3,
                    'connections': {
                        'cc_in': {'pos': 0},
                        'cc_out': {'pos': 2099},
                        'gcb_in': {'pos': 1700},
                        'gcb_out': {'pos': 500}
                        },
                    'heating_rods': {
                        'hr_1': {
                            'pos': 1800,
                            'P_th_stages': [0, 500, 1000, 2000, 3000]
                            }
                        }
                    }
        init_vals : dict
            Initial values for the temperature distribution in the tank or the
            initial el. power of the heating rod.

        Attributes
        ----------
        self.height : ???
            ???
        self.htc_walls : ???
            ???
        self.htc_layers : ???
            ???
        self.T_env : ???
            ???
        self.surface_between_layers : ???
            ???
        self.mass : ???
            ???
        self.layers : []
            ???
        self.connections : dict
            ???
        self.sensors : dict
            ???
        self.heating_rods : dict
            ???
        self._nested_attrs : dict
            ???
        """
        if init_vals is None:
            init_vals = {
                'layers': {'T': 20}
            }
        # default for init_vals
        # model parameters
        self.height = params['height']  # mm
        self.htc_walls = params['htc_walls']
        # heat transfer coefficient to environment in W/(m2K)
        self.htc_layers = params['htc_layers']
        # heat transfer coefficient between layers in W/(m2K)
        self.T_env = params['T_env']  # environment temperature in °C

        if 'diameter' in params:
            diameter = params['diameter']  # mm
        if 'volume' in params:
            diameter = (params['volume'] * 1e6 / (np.pi * self.height)) ** 0.5 * 2

        # only needed during initialization
        self.surface_between_layers = np.pi * (diameter / 3e3) ** 2  # m2

        self.mass = np.pi * (diameter / 2e3) ** 2 * self.height

        # create layers
        self.layers = []
        if 'n_layers' in params:
            if isinstance(init_vals['layers']['T'], list):
                if len(init_vals['layers']['T']) == 2:  # temperature range
                    delta_T = init_vals['layers']['T'][1] - init_vals['layers']['T'][0]
                    T_init = [init_vals['layers']['T'][0] + i * delta_T / (params[
                                                                               'n_layers'] - 1) for i in range(params[
                                                                                                                   'n_layers'])]
                else:
                    T_init = init_vals['layers']['T']
                    if len(T_init) != params['n_layers']:
                        raise ValueError("init_vals['T'] must have %d entries. "
                                         "One for each layer" % params['n_layers'])
            else:
                T_init = [init_vals['layers']['T']] * int(params['n_layers'])
            # create n layers of same height
            h = self.height / params['n_layers']
            for idx in range(params['n_layers']):
                if idx == 0 or idx == params['n_layers'] - 1:
                    bottom_top = True  # True for bottom and top layer
                else:
                    bottom_top = False
                layer_params = {
                    'T': T_init[idx],
                    'bottom': idx * h,
                    'top': (idx + 1) * h,
                    'diameter': diameter,
                    'bottom_top': bottom_top
                }
                self.layers.append(Layer(layer_params))
        elif 'layers' in params:
            # layers are specified explicitly
            n_layers = len(params['layers'])
            if isinstance(init_vals['layers']['T'], list):
                if len(init_vals['layers']['T']) == n_layers:
                    T_init = init_vals['layers']['T']
                else:
                    raise ValueError("init_vals['T'] must have %d entries. "
                                     "One for each layer" % params['n_layers'])
            else:
                T_init = [init_vals['layers']['T']] * n_layers

            for idx, layer_params in enumerate(params['layers']):
                if idx == 0 or idx == n_layers - 1:
                    bottom_top = True  # True for bottom and top layer
                else:
                    bottom_top = False
                layer_params['diameter'] = diameter
                # diameter of each layer is the same, therefore it is specified
                # on the hotwater tank level
                layer_params['bottom_top'] = bottom_top
                layer_params['T'] = T_init[idx]
                self.layers.append(Layer(layer_params))

        # create connections
        self.connections = dict()
        if 'connections' in params:
            for key, connection_params in params['connections'].items():
                self.connections[key] = Connection(connection_params,
                                                   self.layers)
                # reference to layers is needed to have access to layers inside
                # connection methods

        # create sensors
        self.sensors = dict()
        if 'n_sensors' in params:
            # sensors are evenly distributed in hotwater tank
            h = params['height'] / (params['n_sensors'] - 1)
            for i in range(params['n_sensors']):
                if i == params['n_sensors'] - 1:
                    # print('uppermost layer: ', dict(pos=i*h-1))
                    self.sensors['sensor_%02d' % i] = Sensor(
                        dict(pos=i * h - 1), self.layers)
                    # so that the topmost sensor corresponds to the topmost
                    # layer
                else:
                    self.sensors['sensor_%02d' % i] = Sensor(dict(pos=i * h),
                                                             self.layers)

        if 'sensors' in params:
            # sensors are specified explicitly
            for key, value in params['sensors'].items():
                self.sensors[key] = Sensor(value, self.layers)

        # create heating rods
        self.heating_rods = dict()
        if 'heating_rods' in params:
            for key, value in params['heating_rods'].items():
                if key in init_vals:
                    self.heating_rods[key] = HeatingRod(value, self.layers, init_vals[key])
                else:
                    self.heating_rods[key] = HeatingRod(value, self.layers)

        self._nested_attrs = dict()
        # dict to buffer information about nested attributes

    def step(self, step_size, adapted_step_size_mode:bool=False) -> None:
        """
        Perform simulation step with step size step_size
        
        ...

        Parameters
        ----------
        step_size : ???
            ???
        adapted_step_size_mode : bool
            ???
        """

        # update mass flows out of the tank and into
        # the tank

        for key, connection in self.connections.items():

            if not adapted_step_size_mode:
                connection._T_buffer = []
            try:
                if connection.F > 0:
                    if connection.T is not None:
                        connection.corresponding_layer.add_massflow(
                            MassFlow(connection.F, connection.T))
                    else:
                        raise ValueError("temperature of input connection "
                                         "'%s' was not set" % key)
                else:
                    connection.corresponding_layer.add_massflow(
                        MassFlow(connection.F, connection.T))
            except TypeError:
                pass

        # check mass flows
        V_factors = []
        for idx, layer in enumerate(self.layers):
            V_in = layer.inflow * step_size
            V_out = abs(layer.outflow * step_size)
            V = max(V_in, V_out)
            if V > layer.volume:
                V_factors.append(V // layer.volume + (V % layer.volume > 0))

                msg = ('Inflow or outflow per time step into/from layer_%d is '
                       '%.2f l and exceeds layer volume. '
                       'Therefore step size is adapted' % (idx, V))
                # print(msg)

        if V_factors:
            # print(V_factors)
            for layer in self.layers:
                layer.empty_massflows()
            step_size_adapted = step_size / max(V_factors)
            for i in range(0, int(max(V_factors))):
                self.step(step_size_adapted, adapted_step_size_mode=True)
            return

        # calculate massflows between the layers
        for idx, layer in enumerate(self.layers):
            netflow = layer.netflow
            if netflow > 1e-10:
                if idx == len(self.layers) - 1:
                    raise ValueError("Sum of inputs and output flows doesn't "
                                     "equal zero. Check flows!")
                layer.add_massflow(MassFlow(-netflow, layer.T))
                self.layers[idx + 1].add_massflow(MassFlow(netflow,
                                                           layer.T))
            elif netflow < -1e-10:
                if idx == len(self.layers) - 1:
                    raise ValueError("Sum of inputs and output flows doesn't "
                                     "equal zero. Check flows!")
                layer.add_massflow(MassFlow(-netflow,
                                            self.layers[idx + 1].T))
                self.layers[idx + 1].add_massflow(MassFlow(netflow,
                                                           self.layers[idx + 1].T))

        # calculate heatflow to environment
        for idx, layer in enumerate(self.layers):
            # outer_surface = np.pi * layer.diameter / 1e3 * (layer.top
            #        - layer.bottom) / 1e3
            # if idx == 0 or idx == len(self.layers) - 1:
            #    outer_surface += np.pi * (layer.diameter / 2e3)**2
            heatflow = ((self.T_env - layer.T) * layer.outer_surface *
                        self.htc_walls)
            # print('heatflow_layer_%s: %s' % (idx, heatflow))
            layer.add_heatflow(heatflow)

        # calculate heatflow caused by heating rods
        for key, heating_rod in self.heating_rods.items():
            heating_rod.update()
            heating_rod.corresponding_layer.add_heatflow(heating_rod.P_th)

        # calculate heatflow between layers
        for layer, upper_layer in zip(self.layers[:-1], self.layers[1:]):
            # boundary_surface = np.pi * (layer.diameter / 3e3)**2
            heatflow = ((layer.T - upper_layer.T)
                        * self.surface_between_layers * self.htc_layers)
            upper_layer.add_heatflow(heatflow)
            layer.add_heatflow(-heatflow)

        # update temperature of layers
        for layer in self.layers:
            m = layer.volume * RHO
            delta_Q = 0
            for massflow in layer.massflows:
                # print(massflow.T, massflow.F)
                delta_Q += (massflow.F * step_size * RHO * (massflow.T + 273)
                            * C_W)
            # print(layer.heatflows)
            for heatflow in layer.heatflows:
                delta_Q += heatflow * step_size
            layer.T += delta_Q / (m * C_W)
            layer.empty_massflows()
            layer.empty_heatflows()

        # flip temperature if temperature of lower layer is higher
        n_flips = 1
        while n_flips > 0:
            n_flips = 0
            for layer, lower_layer in zip(self.layers[1:], self.layers[:-1]):
                if layer.T < lower_layer.T:
                    n_flips += 1  # count number of flip operations
                    T_buffer = layer.T
                    layer.T = lower_layer.T
                    lower_layer.T = T_buffer

        # update connections
        for key, connection in self.connections.items():
            connection.update(adapted_step_size_mode)

    def get_nested_attr(self, nested_attr):
        """
        Description

        ...

        Parameters
        ----------
        nested_attr : ???
            ???

        Returns
        -------
        ???
            Returns defined attribute
        """
        try:
            name, attr = self._nested_attrs[nested_attr]['parts']
        except KeyError:
            name, attr = nested_attr.split('.')
            self._nested_attrs[nested_attr] = {'parts': (name, attr)}
            if name in self.sensors:
                self._nested_attrs[nested_attr]['type'] = 'sensors'
            elif name in self.heating_rods:
                self._nested_attrs[nested_attr]['type'] = 'heating_rods'
            elif name in self.connections:
                self._nested_attrs[nested_attr]['type'] = 'connections'
            return self.get_nested_attr(nested_attr)

        if_type = getattr(self, self._nested_attrs[nested_attr]['type'])
        return getattr(if_type[name], attr)

    @property
    def snapshot(self):
        """
        Serialize to json
        
        ...

        Returns
        -------
        ???
            ???
        """
        return jsonpickle.encode(self.connections)

    @property
    def T_layers(self):
        """
        Description
        
        ...

        Returns
        -------
        T_layers : list
            ???
        """
        T_layers = []
        for layer in self.layers:
            T_layers.append(layer.T)
        return T_layers

    @property
    def T_sensors(self):
        """
        Description

        ...

        Returns
        -------
        list
            ???
        """
        # T_sensors = []
        keys_sorted = sorted(self.sensors.keys(),
                             key=lambda x: self.sensors[x].pos)
        return [self.sensors[key].T for key in keys_sorted]

    @property
    def T_mean(self):
        """
        Returns mean temperature of hotwatertank in °C
        
        ...
        
        Returns
        -------
        T_mean : float
            ???
        """
        T_sum = 0
        for layer in self.layers:
            T_sum += layer.T
        T_mean = T_sum / len(self.layers)
        return T_mean


class Layer(object):
    """
    Layer of hotwater tank

    :param layer_params: dictionary containing the following keys

        * **T** - initial temperature of layer in °C

        * **bottom** - bottom of layer relatively to hotwater tank bottom in
          mm

        * **top** - top of layer relatively to hotwater tank bottom in mm

        * **diameter** - diameter of layer in mm

        * **bottom_top** - must be True for the bottom or top
          layer of the tank. This information is needed to calculate the outer
          surface of the layer which in turn is needed to calculate heat losses
          to the environment.

    """

    def __init__(self, params:dict) -> None:
        """
        Layer of hotwater tank

        ...

        Parameters
        ----------
        params : dict
            A list of parameters used to set attributes.
            Contains the following keys::

                params = {
                    'T' : 'see attribute'
                    'bottom' : 'see attribute'
                    'top' : 'see attribute'
                    'diameter' : 'see attribute'
                    'bottom_top' : 'must be True for the bottom or top layer of the tank. This information is needed to calculate the outer surface of the layer which in turn is needed to calculate heat losses to the environment.'
                }

        Attributes
        ----------
        self.T : float
            Initial temperature of layer in °C
        self.bottom : float
            Bottom of layer relatively to hotwater tank bottom in mm
        self.top : float
            Top of layer relatively to hotwater tank bottom in mm
        self.diameter : float
            Diameter of layer in mm
        self.outer_surface : float
            The outer surface expressed in m^2
        self.volume : float
            The volume of the tank expressed in liters
        self.massflows : list
            ???
        self.heatflows : list
            ???
        """
        self.T = params['T']  # °C
        self.bottom = params['bottom']  # mm
        self.top = params['top']  # mm
        diameter = params['diameter']  # mm
        self.outer_surface = np.pi * diameter / 1e3 * (self.top
                            - self.bottom) / 1e3 + np.pi * (diameter
                            / 2e3) ** 2 * params['bottom_top']  # m2
        self.volume = np.pi * (diameter / 200) ** 2 * (self.top -
                                                       self.bottom) / 100  # liters
        self.massflows = []
        self.heatflows = []

    def add_massflow(self, massflow) -> None:
        """
        Appends massflow data to the `self.massflows` attribute

        ...

        Parameters
        ----------
        massflow : ???
            ???
        """
        self.__init__()
        if massflow.F != None:
            self.massflows.append(massflow)

    def add_heatflow(self, heatflow) -> None:
        """
        Appends heatflow data to the `self.heatflows` attribute

        ...

        Parameters
        ----------
        heatflow : ???
            ???
        """
        self.heatflows.append(heatflow)

    def empty_massflows(self) -> None:
        """
        Resets `self.massflows` to an empty list
        """
        self.massflows = []

    def empty_heatflows(self) -> None:
        """
        Resets `self.heatflows` to an empty list
        """
        self.heatflows = []

    @property
    def inflow(self) -> float:
        """
        Sums the massflow data to give the inflow

        Returns
        -------
        float
            The sum of `self.massflows` data where the value is greater than 0
        """
        return sum([massflow.F for massflow in self.massflows
                    if massflow.F > 0])

    @property
    def outflow(self) -> float:
        """
        Sums the massflow data to give the outflow

        Returns
        -------
        float
            The sum of `self.massflows` data where the value is less than 0
        """
        return sum([massflow.F for massflow in self.massflows
                    if massflow.F < 0])

    @property
    def netflow(self) -> float:
        """
        Sums the massflow data to give the net flow

        Returns
        -------
        float
            The sum of `self.massflows` data
        """
        return sum([massflow.F for massflow in self.massflows])


class Sensor(object):
    """
    Temperature sensor in the tank.

    :param params: dictionary containing params which specify a sensor, so
        far it contains only one entry *pos*, which defines the position of
        the sensor above hotwater tank bottom

    """

    def __init__(self, params:dict, layers) -> None:
        """
        Temperature sensor in the tank.

        ...

        Parameters
        ----------
        params : dict
            Contains params which specify a sensor, so far it contains 
            only one entry *pos*, which defines the position of the sensor above hotwater tank bottom
        layers : ???
            ???

        Attributes
        ----------
        self.pos : ???
            Defines the position of the sensor above hotwater tank bottom
        """
        self.pos = params['pos']  # mm
        # determine corresponding layer
        for layer in layers:
            if layer.bottom <= self.pos < layer.top:
                self.corresponding_layer = layer
                # reference to corresponding layer

    @property
    def T(self) -> float:  # temperature in °C
        """
        Gets the temperature of the corresponding layer

        Returns
        -------
        self.corresponding_layer.T : float
            The temperature in °C
        """
        return self.corresponding_layer.T


class Connection(object):
    """
    Devices are connected to the hotwater tank via connections.

    Each connection is associated with a :class:`Layer`. For input connections
    (F>0) the correspoding layer is determined by temperature comparison. The
    layer whose temperatue is closest to the connection temperature is the
    corresponding one. For output connections (F<0) the corresponding layer
    depends on the position of the connection.  The corresponding layer of a
    connection is not fix, but may change during the simulation, if the flow or
    temperatures of the connection or the temperature of the layers changes.

    """

    def __init__(self, params:dict, layers) -> None:
        """
        Defines the connections through which devices connect to the hotwater tank

        ...

        Parameters
        ----------
        params : dict
            ???
        layers : ???
            ???
        
        Attributes
        ----------
        self.layers : ???
            ???
        self.pos : ???
            ???
        self.type : ???
            ???
        self._F : float  
            flow [l/s]
        self._T : float 
            Temperature in °C
        self._T_buffer : list
            ???
        self.corresponding_layer : ???
            ??? reference to corresponding layer
        self.corresponding_layer_pos : ???
            ???
        """
        self.layers = layers  # reference to layers
        self.pos = params['pos']
        if 'type' in params:
            self.type = params['type']
        self._F = 0  # flow [l/s]
        self._T = None  # °C
        self._T_buffer = []  # °C
        self.corresponding_layer = None  # reference to corresponding layer
        for idx, layer in enumerate(self.layers):
            if layer.bottom <= self.pos < layer.top:
                self.corresponding_layer_pos = layer
        self.update()

    def update(self, adapted_step_size_mode:bool=False) -> None:
        """
        Description

        ...

        Parameters
        ----------
        adapted_step_size_mode : bool
            ???
        """
        try:
            if self.F <= 0:
                self.corresponding_layer = self.corresponding_layer_pos
                if adapted_step_size_mode:
                    self._T_buffer.append(self.corresponding_layer.T)
            else:  # if self.F > 0:
                delta_T_min = float('Inf')  # smallest difference so far
                for idx, layer in enumerate(self.layers):
                    delta_T = abs(self._T - layer.T)
                    if delta_T < delta_T_min:
                        delta_T_min = delta_T
                        idx_min = idx
                self.corresponding_layer = self.layers[idx_min]
        except TypeError:
            self.corresponding_layer = self.corresponding_layer_pos

    @property
    def T(self) -> float:
        """
        Description
        """
        try:
            if self.F > 0:  # inlet
                return self._T
            elif self.F <= 0:  # outlet
                if self._T_buffer:
                    return (sum(self._T_buffer) / len(self._T_buffer))
                return self.corresponding_layer.T
        except TypeError:
            return self.corresponding_layer.T

    @T.setter
    def T(self, value) -> None:
        """
        Sets the `self._T` value.
        """
        if value != self._T:
            self._T = value
            self.update()  # corresponding layer must be updated

    @property
    def F(self):
        """
        Gets the self._F value

        ...

        Returns
        -------
        self._F : ???
            ???
        """
        return self._F

    @F.setter
    def F(self, value) -> None:
        """
        Sets the self._F value

        ...

        Parameters
        ----------
        value : ???
            ???
        """
        try:
            if self._F <= 0:
                self._F = value
                if value > 0:
                    self.update()
                    # corresponding layer must be only updated on change of sign
            else:
                self._F = value
                if value <= 0:
                    self.update()
                    # corresponding layer must be only updated on change of sign
        except TypeError:
            self._F = value
            self.update()


class MassFlow(object):
    """Massflow"""

    def __init__(self, F, T) -> None:
        """
        Description

        ...

        Parameters
        ----------
        F : ???
            ???
        T : ???
            ???

        Attributes
        ----------
        self.F : ???
            ???
        self.T : ???
            ???
        """
        self.F = F
        self.T = T


class HeatingRod(object):
    """

    Heating rod integrated into to the hotwater tank.

    Heating rods are characterized by their position above tank level and their
    power stages. Efficiency is assumed to be constantly 100%.

    """

    def __init__(self, params, layers, init_vals=None) -> None:
        """
        Heating rod integrated into to the hotwater tank.

        ...

        Parameters
        ----------
        params : dict
            ???
        layers : ???
            ???
        init_vals : ???
            ???

        Attributes
        ----------
        self.pos : ???
            ???
        self.T_max : ???
            ???
        self.P_th_stages : ???
            Power stages in W
        self.eta : ???
            ???
        self.corresponding_layer : ???
            ???
        self.P_th_set : ???
            Set value for thermal power output in W
        self.P_el : ???
            Electric power consumption in W
        self.P_th : ???
            Thermal power output in W
        """
        self.pos = params['pos']
        self.T_max = params['T_max']
        self.P_th_stages = np.array(params['P_th_stages'])  # power stages in W
        self.eta = params['eta']
        for idx, layer in enumerate(layers):
            if layer.bottom <= self.pos < layer.top:
                self.corresponding_layer = layer
                break
        # find corresponding layer
        self.P_th_set = None  # set value for thermal power output in W
        self.P_el = None  # electric power consumption in W
        self.P_th = None  # thermal power output in W
        if init_vals is not None:
            for attr, init_val in init_vals.items():
                if hasattr(self, attr):
                    setattr(self, attr, init_val)
                else:
                    raise AttributeError("init_val %s doesn't match any attribute" % attr)

    def update(self) -> None:
        """
        Description
        """
        if self.corresponding_layer.T < self.T_max:
            idx = np.argmin(abs(self.P_th_stages - self.P_th_set))
            # find closest power stage
            self.P_th = self.P_th_stages[idx]
            self.P_el = -self.P_th/self.eta
        else:
            self.P_th = 0
            self.P_el = 0

    @property
    def P_th_min(self):
        """
        Returns the minimum of the `self.P_th_stages` attribute
        
        Returns
        -------
        self.P_th_stages : ???
            ???
        """
        return self.P_th_stages[0]

    @property
    def P_th_max(self):
        """
        Returns the maximum of the `self.P_th_stages` attribute
        
        Returns
        -------
        self.P_th_stages : ???
            ???
        """
        return self.P_th_stages[-1]

    @property
    def T(self) -> float:
        """
        Gets the temperature of the corresponding layer

        Returns
        -------
        self.corresponding_layer.T : float
            The temperature in °C
        """
        return self.corresponding_layer.T   




