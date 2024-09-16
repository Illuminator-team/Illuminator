"""
Integrating a simulation model into the mosaik ecosystem
"""



# Model creation.
## the strucutre of the model is left to the user


# define a class with your simulation model
class MyModel:
    """Simple model that increases its value *val* with some *delta* every
    step.

    You can optionally set the initial value *init_val*. It defaults to ``0``.
    """

    def __init__(self, init_val=0): # parameters set at instantiation
        # attributes 
        self.val = init_val
        self.delta = 1
        self.time = 0

    def step(self):
        """performs simulation by adding 'delta' to 'val'"""
        self.val += self.delta

