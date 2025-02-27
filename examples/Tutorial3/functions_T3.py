import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime

def plot_load_on_connection(load_df, day, number_houses, tolerance_limit, critical_limit, connection_cap):
    load_houses = load_df * number_houses # scale load with number of houses -> even out/new load profiles

    day_start = datetime.strptime(day, "%Y-%m-%d")
    day_end = day_start.replace(hour=23, minute=45, second=00)
    load_day = load_houses.loc[day_start:day_end]

    plt.plot(load_day.index, load_day['load'], color='black', label='Load', linewidth=2)
    plt.hlines(y = 0, xmin= min(load_day.index), xmax= max(load_day.index), color = 'grey', linestyles='--')
    plt.fill_between(x=load_day.index, y1= (-critical_limit * connection_cap), y2=-connection_cap, color='#F02E31',
                     alpha=0.5, label='Critical Region')
    plt.fill_between(x=load_day.index, y1= (critical_limit * connection_cap), y2=connection_cap, color='#F02E31',
                     alpha=0.5, label='Critical Region')
    plt.fill_between(x=load_day.index, y1=-(tolerance_limit * connection_cap), y2=-(critical_limit * connection_cap),
                     color='#FFE8A2', alpha=0.7, label='Tolerance Region')
    plt.fill_between(x=load_day.index, y1= (tolerance_limit * connection_cap), y2= (critical_limit * connection_cap),
                     color='#FFE8A2', alpha=0.7, label='Tolerance Region')
    plt.fill_between(x=load_day.index, y1= -(tolerance_limit * connection_cap), y2=(tolerance_limit * connection_cap),
                     color='#DAF2D0', alpha=1, label='Good')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.title(f'{day}:Power on Connection')
    plt.xlabel('Time of Day')
    plt.ylabel('Load on Connection (kW)')
    plt.xlim(min(load_day.index), max(load_day.index))
    plt.ylim(-connection_cap, connection_cap)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

def plot_results_connection(results_file, connection_cap, critical_limit, tolerance_limit):

    result_pd_df = pd.read_csv(results_file, index_col=0)
    result_pd_df.index = pd.to_datetime(result_pd_df.index)
    load_on_connection = -result_pd_df['Controller1-0.time-based_0-dump']

    connection_cap = connection_cap
    critical_limit = critical_limit
    tolerance_limit = tolerance_limit

    plt.plot(load_on_connection.index, load_on_connection, color='black', label='Load', linewidth=2)
    plt.hlines(y=0, xmin=min(load_on_connection.index), xmax=max(load_on_connection.index), color='grey', linestyles='--')
    plt.fill_between(x=load_on_connection.index, y1=(-critical_limit * connection_cap), y2=-connection_cap, color='#F02E31',
                     alpha=0.5, label='Critical Region')
    plt.fill_between(x=load_on_connection.index, y1=(critical_limit * connection_cap), y2=connection_cap, color='#F02E31',
                     alpha=0.5, label='Critical Region')
    plt.fill_between(x=load_on_connection.index, y1=-(tolerance_limit * connection_cap),
                     y2=-(critical_limit * connection_cap),
                     color='#FFE8A2', alpha=0.7, label='Tolerance Region')
    plt.fill_between(x=load_on_connection.index, y1=(tolerance_limit * connection_cap), y2=(critical_limit * connection_cap),
                     color='#FFE8A2', alpha=0.7, label='Tolerance Region')
    plt.fill_between(x=load_on_connection.index, y1=-(tolerance_limit * connection_cap),
                     y2=(tolerance_limit * connection_cap),
                     color='#DAF2D0', alpha=1, label='Good')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.title(f':Power on Connection')
    plt.xlabel('Time of Day')
    plt.ylabel('Load on Connection (kW)')
    plt.xlim(min(load_on_connection.index), max(load_on_connection.index))
    plt.ylim(-connection_cap, connection_cap)
    plt.xticks(rotation=45)
    plt.tight_layout()
    #plt.savefig("../Notebooks/T3_Results/grid_connection_winterday_elecassets_loadshift.pdf", format='pdf')
    plt.show()
    return