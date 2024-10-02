class qproduct_python():

    def __init__(self, utilities) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the qdemand_mosaik.qdemandSim class.


        ...

        Parameters
        ----------
        utilities : ???
            ???
        
        Attributes
        ----------
        self.production : int
            ???
        self.utilites : ???
            ???
        """
        self.production = 0
        self.utilities = utilities

    def generation(self, qproduct) -> dict:
        """
        Calculates the generation based on the production and utilities values

        Parameters
        ----------
        qproduct : ???
            ???
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values.
        """
        self.production = self.utilities * qproduct  # m^3/min

        re_params = {'qproduct_gen': self.production}
        return re_params
