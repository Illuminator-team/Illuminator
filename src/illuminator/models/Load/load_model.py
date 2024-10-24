class load_python():

    def __init__(self, houses, output_type,resolution:int=15) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the load_mosaik.loadSim class.


        ...

        Parameters
        ----------
        houses : ???
            ???
        output_type : ???
            ???
        resolution : int
            ???

        Attributes
        ----------
        self.consumption : int
            ???
        self.houses : ???
            ???
        self.output_type : ???
            ???
        self.roslution : ???
            ???
        """
        self.consumption = 0
        self.houses = houses
        self.output_type = output_type
        self.resolution=resolution#min

    def demand(self, load:float) -> dict:
        """
        Performs calculations of load and returns the selected parameters

        ...

        Parameters
        ----------
        load : float
            Incoming load in kWh at every 15 min interval
            
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh

        if self.output_type == 'energy':
            self.consumption = (self.houses * load) # kWh
        elif self.output_type == 'power':
            self.consumption = (self.houses * load)/60*self.resolution # kWh

        re_params = {'load_dem': self.consumption}
        return re_params
