# Creating/writing tests

When it comes to writing tests, the basics are the same between all three types of tests. They all must:

- Have the same 'test' naming convention
- Make some assumptions (assertions) about the code
- Should ideally test not just the positive (happy code / happy flow), but also the negative outcomes of the code


In this section we will create a unit test for the `eboiler` model.

## Writing unit tests

To write a unit test we must first create a python file, import pytest and create a class which will contain all the tests. Let us call the file `test_eboiler_model.py` and the class `TestEboilerModel()`. Based on the name of the file and class, we can see that we are writing tests for the `eboiler_model` file. In addition, since we are testing the `eboiler_python` class within the `eboiler_model` file we should import it. So now the file should look something like this:

```python
import pytest
from illuminator.models.Eboiler.eboiler_model import eboiler_python

class TestEboilerModel():
```

### IMPORTANT NOTE 1
> The file name **MUST** start with "test_" or end with "\_test" in order to be a valid test file. The class must also start with the name "Test", hence why we have chosen the names above. In addition, whenever we create test methods we must also ensure their names start with "test_"

Now let us create our simple test method. We want to test the creation of an `eboiler_model` object. Within `eboiler_model` **__init__()** method (seen below) we see that it expects a dictionary (**eboiler_set:dict**) and that it returns nothing (meaning we do not need to check what it returns)

```python
 def __init__(self, eboiler_set:dict) -> None:
        self.capacity = eboiler_set['capacity']
        self.min_load = eboiler_set['min_load']
        self.max_load = eboiler_set['max_load']
        self.standby_loss = eboiler_set['standby_loss']
        self.efficiency = eboiler_set['efficiency']
        self.resolution = eboiler_set['resolution'] 
```

We can also notice that the dictionary should contain the following key values: [capacity, min_load, max_load, standby_loss, efficiency, resolution]. So we will create some fake data to fill this dictionary with. 
```python
mocked_eboiler_dict = {
    'capacity': 0,
    'min_load': 0,
    'max_load': 100,
    'standby_loss': -0.25,
    'efficiency': 0.33,
    'resolution': 1
}
```

Once created, we may now make our assumptions about what we expect. We expect that the values set within the `eboiler` object will be equal to the values within our **mocked_eboiler_dict** object. We can test this with python's built in function: *assert*

```python
assert eboiler_object.capacity == mocked_eboiler_dict['capacity']
assert eboiler_object.min_load == mocked_eboiler_dict['min_load']
assert eboiler_object.max_load == mocked_eboiler_dict['max_load']
assert eboiler_object.standby_loss == mocked_eboiler_dict['standby_loss']
assert eboiler_object.efficiency == mocked_eboiler_dict['efficiency']
assert eboiler_object.resolution == mocked_eboiler_dict['resolution']
```

With this we have now created a simple test for the `eboiler` object constructor method. The full file should look like this:

```python
import pytest
from illuminator.models.Eboiler.eboiler_model import eboiler_python

class TestEboilerModel():

    # Note that the test must start with 'test_'
    def test_eboiler_constructor(self):
        # Create the fake (mocked) data
        mocked_eboiler_dict = {
            'capacity': 0,
            'min_load': 0,
            'max_load': 100,
            'standby_loss': -0.25,
            'efficiency': 0.33,
            'resolution': 1
        } 

        # Create the eboiler_python object,
        # which automatically calls the __init__() function
        eboiler_object = eboiler_python(mocked_eboiler_dict)


        # What we expect to happen once 
        # we have called the __init__ method above
        assert eboiler_object.capacity == mocked_eboiler_dict['capacity']
        assert eboiler_object.min_load == mocked_eboiler_dict['min_load']
        assert eboiler_object.max_load == mocked_eboiler_dict['max_load']
        assert eboiler_object.standby_loss == mocked_eboiler_dict['standby_loss']
        assert eboiler_object.efficiency == mocked_eboiler_dict['efficiency']
        assert eboiler_object.resolution == mocked_eboiler_dict['resolution']
```

### IMPORTANT NOTE 2
Not every test will be this simple. Some tests will return values which we will also need to check. Other times testing a method will rely on a different method being called. If we do not mock this method then we are no longer writing a unit test. We would instead be stepping into integration testing since by definition, integration testing's purpose is to see how different methods integrate (interact) with one another.

## Mocking

Although the term is sometimes used very loosely to mean "any non-real data and objects", officially mocking is referring to the creation of mock objects (i.e. functions, methods, attributes, environmental variables). For more information on mocking specifically in python (using pytest's monkeypatch), please read the [following documentation](https://docs.pytest.org/en/stable/reference/reference.html).

In order to mock functions/methods, we must first add a new parameter called `monkeypatch` to our test method. This will allow that specific test to mock whatever method we wish.
A simple example of how to mock functions can be found in the code below: 

```python
def test_direct_irr_happy_flow(self, monkeypatch):
        """
        direct_irr multiplies two values together.
                Calculated value, with the given parameters, should be 10
        """
        # Independent mocked methods and variables
        pv = self.create_basic_PV_object() # Helper function to create the PV model
        pv.dni = 10 # Attribute which pv.direct_irr() needs to perform calculations

        # Mocked method (One way of writing is using lambda)
        monkeypatch.setattr(pv, "aoi", lambda: 1) 

        # Another way of writing a mock method
        # def myfunc(*args):
        #     return 1
        # monkeypatch.setattr(pv, "aoi", myfunc)

        # Expected outcome
        expected_dirr = 10
        assert pv.direct_irr() == expected_dirr
```

This was written to test `PV model`'s **direct_irr()** function. In it there are a few things necessary for the function to start. We can find out what will be needed either through a debugger, reading the code, or even trial and error. For this method we need the Independent variables/objects used when calling the **pv.direct_irr(...)** function, such as the actual PV model object and the mandatory value it needs in the calculation: **pv.dni**. Both of those we have created/set manually. 

Finally, there is another function which the `PV model` pv calls called **aoi()**. This is a dependency on a method different than the one we are testing. If we would ignore this function and just let our test do its thing, we would be performing an integration test, not a unit test, thus we need to mock it. By using the **monkeypatch.setattr(object, name, value)** function we tell our test that when the `PV model` object tries to call the **aoi()** function, it will instead just return the value 1.