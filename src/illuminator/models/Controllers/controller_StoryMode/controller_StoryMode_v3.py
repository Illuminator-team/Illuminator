from illuminator.builder import ModelConstructor
from time import sleep

def check_connected(model_name1, model_name2, connections, ids):
    for i, conn in enumerate(connections):
        if conn == (model_name1, model_name2) or conn == (model_name2, model_name1):
            return True, ids[i]
    return False, None
        

# construct the model
class Controller_StoryMode(ModelConstructor):
    """
    Controller for managing power flows between renewable generation, load, and battery storage.
    
    This controller determines how power should be distributed between renewable sources (wind, solar),
    load demands, and battery storage. It implements basic control logic for battery charging and
    discharging based on state of charge limits and power constraints.

    Parameters
    ----------
    soc_min : float
        Minimum state of charge of the battery before discharging stops (%)
    soc_max : float
        Maximum state of charge of the battery before charging stops (%)
    max_p : float
        Maximum power to/from the battery (kW)
    battery_active : bool
        Flag to enable/disable battery operation
    
    Inputs
    ----------
    physical_connections : list
        List of physical connections with ID's of the LED strips

    Outputs
    ----------
    None
    
    States
    ----------
    file_index_Load : int
        Index to select which load file to read from in the CSV model
        
    """
    parameters={}
    inputs={'physical_connections': []}
    outputs={}
    states={'file_index_Load': 0}

    # define other attributes
    time_step_size = 1
    time = None


    def __init__(self, **kwargs) -> None:
        """
        Initialize the Controller model with the provided parameters.

        Parameters
        ----------
        kwargs
        """
        super().__init__(**kwargs)
        self.file_indeces = {'file_index_Load': 0}


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        """
        input_data = self.unpack_inputs(inputs, return_sources=True)  # make input data easily accessible
        self.time = time

        connections, ids = self.determine_connectivity(input_data['physical_connections'])

        to_EWI_LED = []
        to_Ext_LED = []
        to_house_LED = []

        story_phase = 0
        is_connected1, conn_id1 = check_connected('EWI_LED-0.time-based_0', 'Ext_LED-0.time-based_0', connections, ids)
        is_connected2, conn_id2 = check_connected('house_LED-0.time-based_0', 'Ext_LED-0.time-based_0', connections, ids)
        if is_connected1 and not is_connected2:
            print("EWI and Ext connected")
            print("House and Ext connected")
            story_phase = 1
            to_house_LED.append({'from': 'Ext_LED-0.time-based_0', 'to': 'house_LED-0.time-based_0', 'connection_id': conn_id1, 'direction': 1})
            to_EWI_LED.append({'from': 'Ext_LED-0.time-based_0', 'to': 'EWI_LED-0.time-based_0', 'connection_id': conn_id2, 'direction': 1})
            to_Ext_LED.append({'from': 'house_LED-0.time-based_0', 'to': 'Ext_LED-0.time-based_0', 'connection_id': conn_id1, 'direction': -1})
            to_Ext_LED.append({'from': 'house_LED-0.time-based_0', 'to': 'Ext_LED-0.time-based_0', 'connection_id': conn_id1, 'direction': -1})

            self.file_indeces['file_index_Load'] = 1


        self.set_states(self.file_indeces)
        self.set_states({'EWI_LED_mapping': to_EWI_LED, 'Ext_LED_mapping': to_Ext_LED, 'house_LED_mapping': to_house_LED})

        sleep(1)  # simulate some calculation time

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def determine_connectivity(self, physical_connections):
        """
        Determine the connectivity of the LED strips based on the provided physical connections.
        Each LED strip has an ID. If two models have the same ID, they are connected.
        This function function determines model-pairs that are connected based on their IDs.

        Parameters
        ----------
        physical_connections : dict
            

        Returns
        -------
        list of connections
        """
        connections = []
        ids = []
        for i, (id1, model1) in enumerate(zip(physical_connections['value'], physical_connections['sources'])):
            for id2, model2 in zip(physical_connections['value'][i+1:], physical_connections['sources'][i+1:]):
                        # remove -1 before comparing
                set1 = set(id1) - {-1}
                set2 = set(id2) - {-1}
                set1 = set(id1) - {'-1'}
                set2 = set(id2) - {'-1'}
                common_ids = list(set1 & set2)
                if len(common_ids) > 0 and model1 != model2:
                    connections.append((model1, model2))
                    ids.append(common_ids[0])
        print("\n\nconnections: ", connections, "\n\n")
        return connections, ids
        