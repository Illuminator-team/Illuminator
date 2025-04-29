import pandas as pd
import numpy as np

def cost_fun1(df: pd.DataFrame):
    """
    Calculates the sum of the dump column.

    Inputs:
        df: pd.df
            ouput dataframe 
    Returns:
        sum: float
            the sum of a dataframe column
    """
    summed_col = -df['Controller1-0.time-based_0-dump'].sum()
    # summed_col = df['H2_controller-0.time-based_0-dump'].sum()
    return summed_col

def cost_fun_presentation(df: pd.DataFrame, x):
    """
    Calculates the sum of the dump column.

    Inputs:
        df: pd.df
            ouput dataframe 
    Returns:
        sum: float
            times the SoC was 0 and 100
    """
    count_0 = np.isclose(df['H2Buffer1-0.time-based_0-soc'], 0.0).sum()
    count_100 = np.isclose(df['H2Buffer1-0.time-based_0-soc'], 100.0).sum()
    buffer_size = float(x[0])
    if count_0 + count_100 > 0:
        sum = buffer_size * 100
    else:
        sum = buffer_size
    return sum