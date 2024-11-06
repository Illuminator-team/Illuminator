

"""
Load class
xxx=LoadModel(pf_load,'node_1,load_1')
xxx.get(time)
type(time):Timestamp
"""
import pandas as pd

class LoadModel:
    """
    The LoadModel processes and prepares the load profiles and their mate data
    """
    def __init__(self, pf:pd.DataFrame, name) -> None:
        """
        The LoadModel processes and prepares the load profiles and their mate data
        
        ...

        Parameters
        ----------
        pf : pd.Dataframe
            ???
        name : ???
            ???
        
        Attributes
        ----------
        self.data : pd.Dataframe
            ???
        self.name : ???
            ???
        self.lasttime : pd.Series
            ???
        """
        self.data=pf
        self.data['Time']=pd.to_datetime(self.data['Time']) #Timestamp
        self.name=name
        self.lasttime=self.data['Time'].iloc[-1]
        #get the current data

    def get(self, target_time:pd.Timestamp):
        """
        Get the current load for all loads for *minutes* minutes since :attr:`start`.

        ...

        Parameters
        ----------
        target_time : ???
            ???

        Returns
        -------
        ???
            Current load for all loads for *minutes* minutes

        """
        # Trim "minutes" to multiples of "self.resolution"
        # Example: res=15, target_time=2015-02-01 00:18:00 -> target_time=2015-02-01 00:15:00
        # target_time=pd.to_datetime(target_time) #Timestamp
        # target_time.minute=target_time.minute//self.resolution * self.resolution
        if target_time!=self.lasttime:
            cache=self.data.loc[self.data['Time']==target_time]
            target_name=self.name
            #last_dat=cache.iloc[0].loc[target_name]


        else:
            cache = self.data.loc[self.data['Time'] == target_time]
            target_name = self.name
            #last_dat = cache.iloc[0].loc[target_name]
            print('This is last time of Load simulation:', target_time)

        return cache.iloc[0].loc[target_name]

