import pandas as pd


def cost_fun1(df: pd.DataFrame):
    """
    Calculates the sum of the dump column.

    Inputs:
        column: pd.df
            a column of a dataframe
    Returns:
        sum: float
            the sum of a dataframe column
    """
    summed_col = -df['Controller1-0.time-based_0-dump'].sum()
    # summed_col = df['H2_controller-0.time-based_0-dump'].sum()
    return summed_col