class h2product_python():

    def __init__(self, houses) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the h2demand_mosaik.h2demandSim class.

        ...

        Parameters
        ----------
        houses : ???
            ???

        Attributes
        ----------
        self.production : int
            ???
        self.houses : ???
            ???
        """
        self.production = 0
        self.num = houses

    def generation(self, h2product) -> dict:
        """
        Calculates the generatio based on houses and production values

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

        self.production = self.num * h2product  # m^3/min

        re_params = {'h2product_gen': self.production}
        return re_params
