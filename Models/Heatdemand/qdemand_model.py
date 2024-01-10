class qdemand_python():

    def __init__(self, utilities):
        self.consumption = 0
        self.utilites = utilities

    def demand(self, qdemand):


        self.consumption = (self.utilites * qdemand) #m^3/min

        re_params = {'qdemand_dem': self.consumption}
        return re_params
