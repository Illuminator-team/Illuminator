import mosaik_api_v3
import importlib.util

class StateSpaceSimulator(mosaik_api_v3.Simulator):

    #[Manuel] # this can be standardized and must be provided by the model class
    meta = {
        'models': {
            'StateSpaceModel': {  
                'public': True,
                'params': [],  
                'attrs': [],   
                'trigger': [], 
            },
        },
    }

    def __init__(self):
        super().__init__(meta=self.meta)
        self.entities = {}  # Holds the model instances
        self.model_name = None
        self.model_data = None

    def init(self, sid, time_resolution, **sim_params):
        print(f"running extra init")
        # This is the standard Mosaik init method signature
        self.sid = sid
        self.time_resolution = time_resolution

        # Assuming sim_params is structured as {'sim_params': {model_name: model_data}}
        sim_params = sim_params.get('sim_params', {})
        if len(sim_params) != 1:
            raise ValueError("Expected sim_params to contain exactly one model.")

        # Extract the model_name and model_data
        self.model_name, self.model_data = next(iter(sim_params.items()))
        self.model = self.load_model_class(self.model_data['model_path'], self.model_data['model_type'])
        return self.model_data['meta']


    def load_model_class(self, model_path, model_type):
        # Get the module name from the model path, e.g., 'Models/adder_model' -> 'adder_model'
        module_name = model_path.replace('/', '.').rstrip('.py').split('.')[-1]
        
        # Load the module from the specified file path
        spec = importlib.util.spec_from_file_location(module_name, model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Retrieve the class from the module using the model_type
        model_class = getattr(module, model_type)
        
        return model_class

    # [Manuel] # this can be standardized?
    def create(self, num, model, **model_params):
        if num != 1:
            raise ValueError("Can only create one instance of the model.")
        entities = []

        for i in range(num):
            eid = f"{self.model_name}"
            # Create an instance of the model
            model_instance = self.model(
                self.model_data['inputs'], 
                self.model_data['outputs'], 
                self.model_data['parameters'], 
                self.model_data['states'], 
                self.model_data['step_size'], 
                self.model_data['start_time']
            )
            # Store the instance
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': "Model"})

        return entities

    # [Manuel] most be implemented by the model class
    def step(self, time, inputs, max_advance):
        # Update inputs
        for eid, entity_inputs in inputs.items():
            model_instance = self.entities[eid]
            for input_name, input_value in entity_inputs.items():
                model_instance.inputs[input_name] = next(iter(input_value.values()))

        # Step all models
        for model_instance in self.entities.values():
            model_instance.step()

        return time + self.model_data['step_size']


    # [Manuel] this can be standardized
    def get_data(self, outputs):
        data = {}

        for eid, attrs in outputs.items():
            model_instance = self.entities[eid]
            data[eid] = {}
            for attr in attrs:
                if attr in model_instance.outputs:
                    data[eid][attr] = model_instance.outputs[attr]
                else:
                    data[eid][attr] = model_instance.states[attr]

        return data

def main():
    return mosaik_api_v3.start_simulation(StateSpaceSimulator())


if __name__ == '__main__':
    main()
