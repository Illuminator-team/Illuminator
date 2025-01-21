# Custom Model Development

The Illuminator supports and endorses the creation of custom models for your simulation needs. Templates for these models are provided in TODO LINK. Model creation can be done with basic prior programming knowledge and a basic understanding of inheritance and object oriented programming. 

All new models must satisfy the below criteria, this is to ensure a smooth integration and contribution to the Illuminator. Any model created & submitted must fulfill the following conventions to be added to the Illuminator package.

## Good Coding Practices

The points listed in this subsection are general good coding practices already utilised in the Illuminator. We encourage you to adopt these habits for this and any project you are a part of. Such practices directly improve the readability and maintainability of the project.

```python
# Bad Example

def func(x, y):
    return x + y

temp = func(10, 20)
print(temp)

# Good Example

def add_numbers(first_number, second_number):
    return first_number + second_number

result = add_numbers(10, 20)
print(result)
```

### Meaningful Function & Variable Names

Functions and variables should have clean and meaningful names that clearly indicate their purpose and functionality. 

A descriptive name provides context, reduces ambiguity, and eliminates the need for excessive comments to explain its use. Adhering to consistent naming conventions also ensures uniformity across the project and enhances collaboration. 

### Unnecessary Computations

Avoid redundant computations, excessive loops, and duplicate code segments to enhance efficiency and reduce points of error.

Evaluate whether computations can be precomputed, reused, or consolidated to minimize resource consumption. By refactoring repetitive patterns into shared methods, you not only simplify maintenance but also prevent errors caused by inconsistent updates to duplicated logic.

If you come across any such improvement in the existing Illuminator code, we would love to hear them! Contact the main developers at TODO LINK.

### Hard-Coded bits & Spaghetti Code

Hard-coded values and spaghetti code undermine the flexibility and scalability of a project and make debugging and future development exceedingly difficult. Prioritize clean, versatille design. 

### Libraries, Dependencies & Versions

You are welcome to use any library or package in your custom models, try however to not import unused modules or entire libraries when only specific functionalities are required.

```python

# Bad Example:

import pandas  # Entire library is imported but only DataFrame is used

df = pandas.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df)

# Good Example:

from pandas import DataFrame  # Only importing what is needed

df = DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df)

```

Additionally, please ensure you update and specify exact version numbers in dependency manifests (requirements.txt) to ensure that builds are reproducible and unaffected by breaking changes in newer releases.

## Project Documentation

Documentation and code comprehensibility are crucial for an open-source project like the Illuminator. Only through them can contributors and users understand, maintain, and improve the codebase effectively.

### Comments 

Focus on adding comments where the code's purpose or logic is not immediately obvious to the reader. Avoid redundant comments that merely restate the code or clutter the file.

### Docstrings

Docstrings are crucial to custom models because each model's documentation is generated through them. Follow the current style for functions and classes.

The docstrings should have a clearly separated sections for other parts of the code (if any). These may include, but is not limited to: Parameters, Attributes, Returns, Raises. 

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
Docstrings are essential to the Illuminator since each model's documentation is automatically generated through them. It is a model developers responsibility to ensure thorough documentation of their implemented model.

### Consistency & Linting

Always adhere to the conventions and style used in the existing code, including naming patterns, indentation, spacing, and structure. For example, if camelCase is used for variable names, avoid switching to snake_case.

Tools like linters and formatters can help enforce these conventions, this project utilises pylint TODO LINK across its codebase. This package also helps maintain good coding practices mentioned in TODO LINK. Any submitted code must pass pylint's format check.

## Model Testing

This section lists the testing methods you must implement along with your model to verify it operates properly within the rest of the Illuminator framework.

### Scenario Implementation

Creating a YAML scenario file for your custom model is essential for verifying that it integrates and runs properly within the simulation framework. This file essentially acts as a lightweight end-to-end test, providing an easy way to confirm that the model behaves as expected.

### Unit Tests

Unit tests are a critical component of ensuring the internal functionality of your custom model. These tests validate individual methods and components to confirm that they produce the expected outputs for a variety of input cases, including edge scenarios. Further instructions can be found in TODO LINK. 

<!-- ## Missing data in older docstrings
There is still a lot of missing data for older docstrings, which has not been completed due to missing domain knowledge.
In order to contribute to those, one should simply search for any file which contains `???` in its docstrings and change it to whatever is appropriate.
In most cases, the description is missing since we could still acquire datatypes of attributes/parameters based on context clues or debugging/testing. However some bits of code are unused which means that it is also missing the type hints/docstring object types.

There exists an excel sheet within the `docs` folder called `Illuminator Model Classification.xlsx` which contains a semi-filled list of variables and their descriptions which can be used to help finish the incomplete docstrings. -->