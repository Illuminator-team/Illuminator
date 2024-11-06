# Set Up Environment

**Requirements**
* Python >= 3.11
* Recent version of PIP


To set up a development environment:

1. Clone the repository:

```shell
git clone git@github.com:Illuminator-team/Illuminator.git
```

2. Go the root tof the repository:

```shell
cd Illuminator/
```

3. install the development dependencies in editable mode:

```shell 
pip install -e .e
```

## Running Unit Tests

We use `Pytest` to write and test the source code. To run all unit-tests, run the following command at the root of the repository:

```
pytest tests/
```

