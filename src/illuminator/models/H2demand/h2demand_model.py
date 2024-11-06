class h2demand_python:

    def __init__(self, houses ) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the h2demand_mosaik.h2demandSim class.

        ...

        Parameters
        ----------
        houses : ???
            ???

        Attributes
        ----------
        self.consumption : int
            ???
        self.houses : ???
            ???
        """
        self.consumption = 0
        self.houses = houses

    def demand(self, h2demand) -> dict:
        """
        Calculates the consumption based on houses and h2 demand values

        ...

        Parameters
        ----------
        h2demand : ???
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """


        self.consumption = (self.houses * h2demand) #m^3/min

        re_params = {'h2demand_dem': self.consumption}
        return re_params
