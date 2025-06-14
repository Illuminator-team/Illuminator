import pandas as pd
import numpy as np

price_df = pd.read_csv('examples/Lucas_folder/Thesis_comparison2/data/settlement_prices_2023_TenneT_DTS.csv', skiprows=1)

# df = pd.read_csv('./examples/Lucas_folder/Thesis_comparison2/out_CSV.csv')

# dump = df['Controller1-0.time-based_0-dump']

# price_short = price_df['Price_Shortage'][:len(dump)]
# price_surplus = price_df['Price_Surplus'][:len(dump)]
# cost = pd.Series(np.where(dump > 0, dump * -price_surplus, -dump*price_short))
# tot_cost = cost.sum()

# print(f'length of price_short: {len(price_short)}')
# print(f'head of price_short: {price_short.head()}')
# print(f'length of price_surplus: {len(price_surplus)}')
# print(f'head of price_surplus: {price_surplus.head()}')
# print(f'length of dump: {len(dump)}')
# print(f'tot_cost: {tot_cost}')



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

def cost_fun2(df: pd.DataFrame):
    """
    Calculates the sum of the dump column times the variable price.

    Inputs:
        df: pd.df
            ouput dataframe 
    Returns:
        cost: float
            the stotal cost of the specified time period
    """
    dump = df['Controller1-0.time-based_0-dump']
    
    price_short = price_df['Price_Shortage'][:len(dump)]
    price_surplus = price_df['Price_Surplus'][:len(dump)]
    cost = pd.Series(np.where(dump > 0, dump * -price_surplus, -dump*price_short))
    tot_cost = cost.sum()
 
    return tot_cost

def cost_fun_presentation(df: pd.DataFrame, x):
    """
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

def optimal_buffer_size(df: pd.DataFrame, x):
    """
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
    penalty_factor = 1e3  # How strongly you penalize SoC violations
    violation_penalty = (count_0 + count_100) * penalty_factor

    # Objective: minimize size while avoiding extremes
    cost = buffer_size + violation_penalty

    return cost



# x = [102]
# df = pd.read_csv("./examples/Lucas_folder/Thesis_comparison1/temp_out/thesis_comparison_hydrogen_monthly_154443616426_473a1654a041_102.csv")
# print(df['H2Buffer1-0.time-based_0-soc'].dtype)
# print("THIS IS COST FUN:", cost_fun_presentation(df, x))