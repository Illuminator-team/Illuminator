import pandas as pd


def cost_fun1(column: pd.Series):
    """
    Simply calculates the total sum of one column of the output,
    for example the total power pulled from the grid, or the 
    total flared hydrogen.

    Inputs:
        column: pd.df
            a column of a dataframe
    Returns:
        sum: float
            the sum of a dataframe column
    """
    sum = column.sum
    return sum