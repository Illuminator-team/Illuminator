import mosaik_api_v3
try:
    from models.state_space_model import Model as model # Modify model.state_space_model to  model.<model_name>_model
except ImportError:
    from state_space_model import Model as model # Modify model.state_space_model to  model.<model_name>_model
else:
    raise ImportError('Model not found.')
# END OF IMPORTS

""" Mandatory prefilled .yaml file
- name: Batteries
  path: 'Models/state_space_model.py' # path to the models's code
  models: 
  - name: Battery1
    Inputs: [demand_power_flow=0] # Positive values are charging, negative values are discharging
    Outputs: [effective_power_flow=0] # effective_power_flow is the actual power flow
    Parameters: [capacity=1000] # capacity is the battery capacity in kWh
    States: [soc=500]  # soc is the state of charge in kWh
"""

META = {
    'type': 'time-based',
    'models': {
        'SSM_Example': {
            'public': True,
            'params': ['soc', 'capacity'],
            'attrs': ['requested_power_flow', 'effective_power_flow', 'soc'],
        },
    },
}

class StateSpaceSimulator(mosaik_api_v3.Simulator):
    """
    A simulator class representing a state space model. To illustrate we implemented a simple battery.

    To use your own model you must:
    1) Files:
        - Make a new folder in the models directory with the name of your model.
        - Copy the state_space_simulator.py and state_space_model.py into the new folder.
        - Modify the name of the file as such: <model_name>_simulator.py and <model_name>_model.py.
    2) Simulator:
        - Change the model import to point to your model.
        - Modify the META dictionary:
            - Include the model name.
            - Include the model parameters, which in a SSM model are the states + parameters.
            - Include the model attributes, which in a SSM model are the inputs + outputs.
        - Modify the empty .yaml file at the top:
            - Include the model name.
            - Include the model inputs. Make sure to select good default values, that ensure stability. Or set the default to None.
            - Include the model outputs. Make sure to select good default values, that ensure stability. Or set the default to None.
            - Include the model parameters. Set relevant default values and explain the meaning of the parameters and when the defaults are valid.
            - Include the model states. Set relevant default values and explain the meaning of the states and when the defaults are valid.
    3) Model:
        - Modify the model to include the model logic.
        - Modify the model to include the model step function.

    Attributes:
        entities (dict): A dictionary storing all instances of this model by ID.

    Methods:
        init(sid, model, model_name, step_size):
            Initializes the state space model.

        create(num, inputs, outputs, parameters, states):
            Creates multiple entities of the model.

        step(time, inputs):
            Processes inputs and steps the model.

        get_data(outputs):
            Retrieves output data from the model.
    """
    def __init__(self):
        super().__init__(META)
        self.entities = {}  # Stores all instances of this model by ID

    def init(self, sid, step_size, model_name):
        self.sid = sid # Store the simulation ID
        self.model = model # Pointer to model to create such as: 'Battery', 'PV', 'Wind', etc.
        self.model_name = model_name # Store the model name to ensure uniqueness of entity IDs. Sometimes called eid_prefix.
        self.step_size = step_size # Store the step size
        return self.meta

    def create(self, num, inputs, outputs, parameters, states):
        # Create num entities
        entities = []
        for i in range(num):
            eid = f'{self.model_name}_{i}' # Create unique entity ID
            new_model = self.model( # Create a new model instance, passing the inputs, outputs, parameters, and states
                inputs=inputs,
                outputs=outputs,
                parameters=parameters,
                states=states
            )
            self.entities[eid] = new_model # Store the model instance internally
            entities.append({'eid': eid, 'type': self.model}) # Append the entity ID and type to the list of entities
        return entities 

    def step(self, time, inp                        uts):
        self.time = time
        # Process inputs and step the model
        for eid, entity_inputs in inputs.items():
            current_model = self.entities[eid] # Get the model instance
            # Update the inputs
            for attr, value in entity_inputs.items():
                current_model.inputs[attr] = value

            # Perform a simulation step
            current_model.step()

        return time + self.step_size

    def get_data(self, outputs):
        data = {} # Create a dictionary to store the output data
        data['time'] = self.time
        for eid, attrs in outputs.items():
            model = self.entities[eid] # Get the model instance
            data[eid] = {}
            for attr in attrs:
                # Get model outputs:
                try:
                    data[eid][attr] = getattr(model, attr) # Get the attribute value from the model instance
                except ValueError as e:
                    print(f'Error getting attribute {attr} for entity {eid}: {e}') # Log an error if the attribute is not found
        return data
    

def main():
    return mosaik_api_v3.start_simulation(StateSpaceSimulator())


if __name__ == '__main__':
    main()