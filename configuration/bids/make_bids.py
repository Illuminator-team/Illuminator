
import random
from datetime import datetime, timedelta

# Function to generate data
def generate_data(start_date, end_date, bid_range, num_bids_per_day, mc_range) -> list:
    """
    Unknown description.
    Not used by any of the 5 test cases

    ...

    Parameters
    ----------
    start_date : ???
        ???
    end_date : ???
        ???
    bid_range : ???
        ???
    num_bids_per_day : ???
        ???
    mc_range : ???
        ???

    Returns
    -------
    data : list
        Description
    """
    current_date = start_date
    data = []
    while current_date <= end_date:
        for _ in range(num_bids_per_day):
            time = current_date.strftime("%Y-%m-%d %H:%M:%S")
            bid = random.uniform(*bid_range)
            mc = random.uniform(*mc_range)  # Generate random marginal cost
            data.append([time, bid, mc])  # Store marginal cost instead of num_bids_per_day
        current_date += timedelta(minutes=15)
    return data

# Define your parameters
start_date = datetime(2012, 4, 15, 0, 0)
end_date = datetime(2012, 4, 16, 0, 0)
supply_bid_range = (1, 20)  # bid will be a random number between these values
demand_bid_range = (1, 20)  # different bid range for demand
supply_num_bids_per_day = 4 # number of bids per hour
demand_num_bids_per_day = 4 # number of bids per hour
mc_range = (0.10, 0.40)  # range of possible marginal costs
mb_range = (0.1, 0.4)  # range of possible marginal benefit

# Generate your data
supply_bids = generate_data(start_date, end_date, supply_bid_range, supply_num_bids_per_day, mc_range)
demand_bids = generate_data(start_date, end_date, demand_bid_range, demand_num_bids_per_day, mb_range)
def write_data_to_file(data, bid_type, file) -> None:
    """
    Unknown description.
    Not used by any of the 5 test cases

    ...

    Parameters
    ----------
    data : ???
        ???
    bid_type : ???
        ???
    file : ???
        ???
    """
    file.write(f"{bid_type} =")
    file.write("[")
    for i, bid in enumerate(data):
        if i == len(data) - 1:  # If it's the last bid, we close the brackets
            file.write(str(bid) + "]\n")
        elif data[i+1][0] != bid[0]:  # If the next bid is from a different day, we change lines
            file.write(str(bid) + ",\n")
        else:  # If the next bid is from the same day, we just add a comma
            file.write(str(bid) + ", ")

# Write your data to file
with open('initial_bids.py', 'w') as file:
    write_data_to_file(supply_bids, 'initial_supply_bids', file)
    write_data_to_file(demand_bids, 'initial_demand_bids', file)
