# Docstrings

The entirety of this project follows the [Numpy docstring style guide](https://numpydoc.readthedocs.io/en/latest/format.html), so for more information or questions please refer to the provided link.

## Short summary

The style guide states that all comments should start with triple quotation marks, seen below:

```python
def add(a, b):
    """
    The sum of two numbers.
    """
    return a + b
```

The docstrings should also have a clearly separated sections for other parts of the code (if any). These may include, but is not limited to: Parameters, Attributes, Returns, Raises. 

Each separated section should start with the Title of the section, followed by a row of dashes such as in the following section:

```python
def multiply(a, b):
    """
    Computes the multiplication of two numbers and returns its value.

    ...
    Parameters
    ----------
    a : int
        The first integer of the multiplication formula
    b : int
        The second integer of the multiplication formula

    Returns
    -------
    int
        The two values multiplied.
    """
    return a * b
```

When appropriate, we should also ensure to include the name and/or type of variables for the any of the aforementioned sections. 

Lastly, type hints are also a useful addition to any code. They can be used to "hint" to other developers what is expected as input and/or output when a function is used. 
```python
def sum(a:int, b:int) -> float:
```
As seen from the example above we can immediately conclude that for this function to work it will need an integer `a` and `b`, with the return value being of type float

Combined, the docstrings may look something like this:

```python
def sum(a:int, b:int) -> float:
    """
    Computes the sum of `a` and `b` and returns the outcome

    ...

    Parameters
    ----------
    a : int
        The first integer of the sum formula
    b : int
        The second integer of the sum formula

    Returns
    -------
    result : float
        The sum of a + b
    """
    result = a + b
    return result
```

## Missing data in older docstrings
There is still a lot of missing data for older docstrings, which has not been completed due to missing domain knowledge.
In order to contribute to those, one should simply search for any file which contains `???` in its docstrings and change it to whatever is appropriate.
In most cases, the description is missing since we could still acquire datatypes of attributes/parameters based on context clues or debugging/testing. However some bits of code are unused which means that it is also missing the type hints/docstring object types.

There exists an excel sheet within the `docs` folder called `Illuminator Model Classification.xlsx` which contains a semi-filled list of variables and their descriptions which can be used to help finish the incomplete docstrings.