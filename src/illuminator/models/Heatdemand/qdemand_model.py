class qdemand_python():

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
        self.consumption : int
            ???
        self.utilites : ???
            ???
        """
        self.consumption = 0
        self.utilites = utilities

    def demand(self, qdemand) -> dict:
        """
        Calculates the consumption based on the demand and utilities values

        Parameters
        ----------
        qdemand : ???
            ???
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values.
        """

        self.consumption = (self.utilites * qdemand) #m^3/min

        re_params = {'qdemand_dem': self.consumption}
        return re_params
