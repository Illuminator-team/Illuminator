# Set Up Environment
Follow these steps to set up a development environment.

**Requirements**
* Python >= 3.11
* Recent version of PIP

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
pip install -e .
```

## Running Unit Tests

We use `Pytest` to write and test the source code. To run all unit-tests, run the following command at the root of the repository:

```shell
pytest tests/
```

