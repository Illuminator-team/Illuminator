import datetime

import pandas as pd

DATE_FORMAT = ['YYYY-MM-DD HH:mm', 'YYYY-MM-DD HH:mm:ss']
"""Date format used to convert strings to dates."""

class LoadModel:
    def __init__(self,meta,profile):
        """
        Used in Python based Mosaik simulations as an addition to the mosaik-model.LoadholdSim class.

        ...

        Parameters
        ----------
        meta : dict
            The initial metadata
        profile : pd.DataFrame
            ???
        
        Attributes
        ----------
        self.start : ???
            ???
        self.resolution : ???
            Resolution unit:min
        self.unit : ???
            ???
        self.load_ids : list
            Obtain id lists
        self.loads : list
            ???
        self.data : ???
            ???
        self._data : pd.DataFrame
            The data at minutes
        self._last_date : ???
            Last time instance
        self._cache : series
            Load power at cache
        """
        #data={'start':'2015-02-01 00:00:00','resolution':15*60,'unit':'W'}
        #profile=dataframe of load profile
        self.start=meta['start']
        self.resolution=meta['resolution']#resolution unit:min
        self.unit=meta['unit']
        #obtain id lists
        self.load_ids= profile.iloc[0].index[1:].to_list()
        #load_ids=['Load R1','Load R2']

        self.loads=[
            {
                #'load_num': i+1,
                'load_id':n,
            }for i,n in enumerate(self.load_ids)
        ]
        self.data=profile
        self.data['Time']=pd.to_datetime(self.data['Time'])#change time to 'timestamp'
        #variables for get()
        self._data=None#the data at minutes(dataFrame)
        self._last_date=None#last time instance
        self._cache=None#load power at cache

    def get(self,minutes:int):
        """
        Get the current load power for all loads at minutes since attr:'start'.

        Parameters
        ----------
        minutes : int
            The minutes at which the load will be acquired
        
        Returns
        --------
        series
            load power at cache

        Notes
        -----
        If the model uses a 15min resolution and minutes not multiple of 15,
        the next smaller multiple of 15 will be used. For example, if you
        pass ``minutes=23``, you'll get the value for ``15``.
        """

        # Trim "minutes" to multiples of "self.resolution"
        # Example: res=15, minutes=40 -> minutes == 30
        minutes = minutes // self.resolution * self.resolution
        target_data=pd.to_datetime(self.start)+datetime.timedelta(minutes=minutes)
        last_data=self.data['Time'].iloc[-1]
        if target_data>last_data:
            raise IndexError('Target date "%s" (%s minutes from start) '
                             'out of range.' % (target_data, minutes))
        else:
            self._last_date=target_data
            self._data=self.data[self.data['Time']==target_data]
            just_cache=self._data.drop(['Time'],axis=1)
            self._cache=just_cache.iloc[0]

        #return series nload_1:  1.0, load_2:    1.0
        return self._cache


    def get_delta(self,date:str) -> int:
        """
        Get the amount of minutes between *date* and :attr:`start`.

        Parameters
        ----------
        date : str
            A string formated like :data:`DATE_FORMAT`.
        
        Raises
        ------
        ValueError
            Raise a :exc:`ValueError` if *date* is smaller than :attr:`start`.
        
        Returns
        -------
        minutes : int
            The number of minutes
        """
        start_timestep=pd.to_datetime(self.start)
        getdate_timestep=pd.to_datetime(date)
        if getdate_timestep<start_timestep:
            raise ValueError('date must >= "%s".' %
                             self.start.format(DATE_FORMAT))

        dt=getdate_timestep-start_timestep
        minutes = (dt.days * 1440) + (dt.seconds // 60)
        return minutes













