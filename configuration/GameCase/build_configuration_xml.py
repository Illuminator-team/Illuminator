import pandas as pd



sim_config=[['Wind' ,'python','Models.Wind.wind_mosaik:WindSim'],
            ['PV' ,'python', 'Models.PV.pv_mosaik:PvAdapter'],
            ['Load', 'python', 'Models.Load.load_mosaik:loadSim'],
            ['Collector', 'python', 'Models.collector:Collector'],
            ['CSVB', 'python', 'Models.mosaik_csv:CSV'],
            ['ElectricityNetwork', 'python', 'Models.Elenetwork.electricity_network_mosaik:electricitynetworkSim'],
            ['Battery', 'python', 'Models.Battery.battery_mosaik:BatteryholdSim'],
            ['Electrolyser', 'python', 'Models.Electrolyser.electrolyser_mosaik:ElectrolyserSim'],
            ['H2storage', 'python', 'Models.H2storage.h2storage_mosaik:compressedhydrogen'],
            ['Fuelcell', 'python', 'Models.Fuelcell.fuelcell_mosaik:FuelCellSim'],
            ['GPController','python', 'Controllers.GPController.gpcontroller_mosaik:gpcontrolSim'],   #gpcontrol
            ['Prosumer','python', 'Agents.prosumer_mosaik:prosumerSim'],
            ['Emarket','python', 'Games.emarket_mosaik:emarketSim'],
            ['P2Ptrading','python', 'Games.p2ptrading_mosaik:p2ptradingSim'],
            ['RTprice','python', 'Games.rtprice_mosaik:rtpriceSim']
            ]
sim_config_df=pd.DataFrame(sim_config, columns=['model','method','location'])
sim_config_data=sim_config_df.to_xml()

with open('../../Cases/GameCase/config.xml','w') as file:
    file.write(sim_config_data)


connection = [
 # Agent 0 -------------------------------------------------------------------------------------

    # Load
    ['load[0]', 'gpctrl[0]', 'load_dem', 'demand[0]'],
    ['load[0]', 'monitor', 'load_dem','load_dem'],
    ['gpctrl[0]', 'prosumer_s1[0]', 'demand[0]', 'demand[0]'],
    ['gpctrl[0]', 'monitor', 'demand[0]','demand[0]'],

    # Wind
    ['wind[0]', 'gpctrl[0]', 'wind_gen', 'generator[0]'],
    ['wind[0]', 'monitor', 'wind_gen','wind_gen'],
    ['gpctrl[0]', 'prosumer_s1[0]', 'generator[0]', 'generator[0]'],
    ['gpctrl[0]', 'monitor', 'generator[0]','generator[0]'],

    # PV
    ['pv[0]', 'gpctrl[0]', 'pv_gen', 'generator[1]'],
    ['pv[0]', 'monitor', 'pv_gen','pv_gen'],
    ['gpctrl[0]', 'prosumer_s1[0]', 'generator[1]', 'generator[1]'],
    ['gpctrl[0]', 'monitor', 'generator[1]','generator[1]'],

    # Gpctrl
    ['gpctrl[0]', 'monitor', 'net','net'],
    ['gpctrl[0]', 'monitor', 'excess','excess'],
    ['gpctrl[0]', 'monitor', 'deficit','deficit'],

    # Agent 1 -------------------------------------------------------------------------------------

    # Load
    ['load[1]', 'gpctrl[1]', 'load_dem', 'demand[0]'],
    ['load[1]', 'monitor', 'load_dem','load_dem'],
    ['gpctrl[1]', 'prosumer_s1[1]', 'demand[0]', 'demand[0]'],
    ['gpctrl[1]', 'monitor', 'demand[0]','demand[0]'],

    # PV
    ['pv[1]', 'gpctrl[1]', 'pv_gen', 'generator[0]'],
    ['pv[1]', 'monitor', 'pv_gen','pv_gen'],
    ['gpctrl[1]', 'prosumer_s1[1]', 'generator[0]', 'generator[0]'],
    ['gpctrl[1]', 'monitor', 'generator[0]','generator[0]'],

    # Gpctrl
    ['gpctrl[1]', 'monitor', 'net','net'],
    ['gpctrl[1]', 'monitor', 'excess','excess'],
    ['gpctrl[1]', 'monitor', 'deficit','deficit'],

    # Agent 2 -----------------------------------------------------------------------------------

    # Load
    ['load[2]', 'gpctrl[2]', 'load_dem', 'demand[0]'],
    ['load[2]', 'monitor', 'load_dem','load_dem'],
    ['gpctrl[2]', 'prosumer_s1[2]', 'demand[0]', 'demand[0]'],
    ['gpctrl[2]', 'monitor','demand[0]' ,'demand[0]'],

    # Wind
    ['wind[1]', 'gpctrl[2]', 'wind_gen', 'generator[0]'],
    ['wind[1]', 'monitor', 'wind_gen','wind_gen'],
    ['gpctrl[2]', 'prosumer_s1[2]', 'generator[0]', 'generator[0]'],
    ['gpctrl[2]', 'monitor', 'generator[0]','generator[0]'],

    # Battery
    ['battery[0]', 'gpctrl[2]', 'soc', 'storage[0]'],
    ['battery[0]', 'monitor', 'soc','soc'],
    ['battery[0]', 'monitor', 'flow2b','flow2b'],
    ['gpctrl[2]', 'prosumer_s1[2]', 'storage[0]', 'storage[0]'],
    ['gpctrl[2]', 'monitor', 'storage[0]','storage[0]'],
    ['gpctrl[2]', 'battery[0]', 'flow2b[0]', 'flow2b','time_shifted=True'],
    ['gpctrl[2]', 'monitor', 'flow2b[0]','flow2b[0]'],

    # PV
    ['pv[2]', 'gpctrl[2]', 'pv_gen', 'generator[1]'],
    ['pv[2]', 'monitor', 'pv_gen','pv_gen'],
    ['gpctrl[2]', 'prosumer_s1[2]', 'generator[1]', 'generator[1]'],
    ['gpctrl[2]', 'monitor', 'generator[1]','generator[1]'],

    # Gpctrl
    ['gpctrl[2]', 'monitor', 'net','net'],
    ['gpctrl[2]', 'monitor', 'excess','excess'],
    ['gpctrl[2]', 'monitor', 'deficit','deficit'],

    # Agent 3 -----------------------------------------------------------------------------------

    # Load
    ['load[3]', 'gpctrl[3]', 'load_dem', 'demand[0]'],
    ['load[3]', 'monitor', 'load_dem','load_dem'],
    ['gpctrl[3]', 'prosumer_s1[3]', 'demand[0]', 'demand[0]'],
    ['gpctrl[3]', 'monitor', 'demand[0]','demand[0]'],

    # PV
    ['pv[3]', 'gpctrl[3]', 'pv_gen', 'generator[0]'],
    ['pv[3]', 'monitor', 'pv_gen','pv_gen'],
    ['gpctrl[3]', 'prosumer_s1[3]', 'generator[0]', 'generator[0]'],
    ['gpctrl[3]', 'monitor', 'generator[0]','generator[0]'],

    # Gpctrl
    ['gpctrl[3]', 'monitor', 'net','net'],
    ['gpctrl[3]', 'monitor', 'excess','excess'],
    ['gpctrl[3]', 'monitor', 'deficit','deficit'],

    # Agent 4 -------------------------------------------------------------------------------------

    # Load
    ['load[4]', 'gpctrl[4]', 'load_dem', 'demand[0]'],
    ['load[4]', 'monitor', 'load_dem','load_dem'],
    ['gpctrl[4]', 'prosumer_s1[4]', 'demand[0]', 'demand[0]'],
    ['gpctrl[4]', 'monitor', 'demand[0]','demand[0]'],

    # Wind
    ['wind[2]', 'gpctrl[4]', 'wind_gen', 'generator[0]'],
    ['wind[2]', 'monitor', 'wind_gen','wind_gen'],
    ['gpctrl[4]', 'prosumer_s1[4]', 'generator[0]', 'generator[0]'],
    ['gpctrl[4]', 'monitor', 'generator[0]','generator[0]'],

    # PV
    ['pv[4]', 'gpctrl[4]', 'pv_gen', 'generator[1]'],
    ['pv[4]', 'monitor', 'pv_gen','pv_gen'],
    ['gpctrl[4]', 'prosumer_s1[4]', 'generator[1]', 'generator[1]'],
    ['gpctrl[4]', 'monitor', 'generator[1]','generator[1]'],

    # Gpctrl
    ['gpctrl[4]', 'monitor', 'net','net'],
    ['gpctrl[4]', 'monitor', 'excess','excess'],
    ['gpctrl[4]', 'monitor', 'deficit','deficit'],

    # Agent 5 -----------------------------------------------------------------------------------

    # Load
    ['load[5]', 'gpctrl[5]', 'load_dem', 'demand[0]'],
    ['load[5]', 'monitor', 'load_dem','load_dem'],
    ['gpctrl[5]', 'prosumer_s1[5]', 'demand[0]', 'demand[0]'],
    ['gpctrl[5]', 'monitor', 'demand[0]','demand[0]'],

    # PV
    ['pv[5]', 'gpctrl[5]', 'pv_gen', 'generator[0]'],
    ['pv[5]', 'monitor', 'pv_gen','pv_gen'],
    ['gpctrl[5]', 'prosumer_s1[5]', 'generator[0]', 'generator[0]'],
    ['gpctrl[5]', 'monitor', 'generator[0]','generator[0]'],

    # Gpctrl
    ['gpctrl[5]', 'monitor', 'net','net'],
    ['gpctrl[5]', 'monitor', 'excess','excess'],
    ['gpctrl[5]', 'monitor', 'deficit','deficit'],

    # -- Games --------------------------------------------------------------------------------------

    # RT price --------------------------------------------------------------------------------------
    ['rtprice[0]', 'monitor', 'buy_price','buy_price'],
    ['rtprice[0]', 'monitor', 'sell_price','sell_price'],

    # Agent 0 in RT price
    ['prosumer_s1[0]', 'rtprice[0]', 'rt_buy', 'buy[0]'],
    ['prosumer_s1[0]', 'rtprice[0]', 'rt_sell', 'sell[0]'],
    ['prosumer_s1[0]', 'monitor', 'rt_buy','rt_buy'],
    ['prosumer_s1[0]', 'monitor', 'rt_sell','rt_sell'],

    # Agent 1 in RT price
    ['prosumer_s1[1]', 'rtprice[0]', 'rt_sell', 'sell[1]'],
    ['prosumer_s1[1]', 'rtprice[0]', 'rt_buy', 'buy[1]'],
    ['prosumer_s1[1]', 'monitor', 'rt_buy','rt_buy'],
    ['prosumer_s1[1]', 'monitor', 'rt_sell','rt_sell'],

    # Agent 2 in RT price
    ['prosumer_s1[2]', 'rtprice[0]', 'rt_sell', 'sell[2]'],
    ['prosumer_s1[2]', 'rtprice[0]', 'rt_buy', 'buy[2]'],
    ['prosumer_s1[2]', 'monitor', 'rt_buy','rt_buy'],
    ['prosumer_s1[2]', 'monitor', 'rt_sell','rt_sell'],

    # Agent 3 in RT price
    ['prosumer_s1[3]', 'rtprice[0]', 'rt_sell', 'sell[3]'],
    ['prosumer_s1[3]', 'rtprice[0]', 'rt_buy', 'buy[3]'],
    ['prosumer_s1[3]', 'monitor', 'rt_buy','rt_buy'],
    ['prosumer_s1[3]', 'monitor', 'rt_sell','rt_sell'],

    # Agent 4 in RT price
    ['prosumer_s1[4]', 'rtprice[0]', 'rt_sell', 'sell[4]'],
    ['prosumer_s1[4]', 'rtprice[0]', 'rt_buy', 'buy[4]'],
    ['prosumer_s1[4]', 'monitor', 'rt_buy','rt_buy'],
    ['prosumer_s1[4]', 'monitor', 'rt_sell','rt_sell'],

    # Agent 5 in RT price
    ['prosumer_s1[5]', 'rtprice[0]', 'rt_sell', 'sell[5]'],
    ['prosumer_s1[5]', 'rtprice[0]', 'rt_buy', 'buy[5]'],
    ['prosumer_s1[5]', 'monitor', 'rt_buy','rt_buy'],
    ['prosumer_s1[5]', 'monitor', 'rt_sell','rt_sell'],

    # --- Emarket ----------------------------------------------------------------------------------------------
    ['emarket[0]', 'monitor', 'market_price','market_price'],
    ['emarket[0]', 'monitor', 'market_quantity','market_quantity'],

    # Agent 0 in Emarket
    ['prosumer_s1[0]', 'emarket[0]', 'em_supply_bids', 'supply_bids[0]'],
    ['prosumer_s1[0]', 'emarket[0]', 'em_demand_bids', 'demand_bids[0]'],
    ['emarket[0]', 'prosumer_s1[0]', 'accepted_bids', 'em_accepted_bids','time_shifted=True'],
    ['prosumer_s1[0]', 'monitor', 'p2em','p2em'],

    # Agent 1 in Emarket
    ['prosumer_s1[1]', 'emarket[0]', 'em_supply_bids', 'supply_bids[1]'],
    ['prosumer_s1[1]', 'emarket[0]', 'em_demand_bids', 'demand_bids[1]'],
    ['emarket[0]', 'prosumer_s1[1]', 'accepted_bids', 'em_accepted_bids','time_shifted=True'],
    ['prosumer_s1[1]', 'monitor', 'p2em','p2em'],

    # Agent 2 in Emarket
    ['prosumer_s1[2]', 'emarket[0]', 'em_supply_bids', 'supply_bids[2]'],
    ['prosumer_s1[2]', 'emarket[0]', 'em_demand_bids', 'demand_bids[2]'],
    ['emarket[0]', 'prosumer_s1[2]', 'accepted_bids', 'em_accepted_bids','time_shifted=True'],
    ['prosumer_s1[2]', 'monitor', 'p2em','p2em'],

    # Agent 3 in Emarket
    ['prosumer_s1[3]', 'emarket[0]', 'em_supply_bids', 'supply_bids[3]'],
    ['prosumer_s1[3]', 'emarket[0]', 'em_demand_bids', 'demand_bids[3]'],
    ['emarket[0]', 'prosumer_s1[3]', 'accepted_bids', 'em_accepted_bids','time_shifted=True'],
    ['prosumer_s1[3]', 'monitor', 'p2em','p2em'],

    # Agent 4 in Emarket
    ['prosumer_s1[4]', 'emarket[0]', 'em_supply_bids', 'supply_bids[4]'],
    ['prosumer_s1[4]', 'emarket[0]', 'em_demand_bids', 'demand_bids[4]'],
    ['emarket[0]', 'prosumer_s1[4]', 'accepted_bids', 'em_accepted_bids','time_shifted=True'],
    ['prosumer_s1[4]', 'monitor', 'p2em','p2em'],

    # Agent 5 in Emarket
    ['prosumer_s1[5]', 'emarket[0]', 'em_supply_bids', 'supply_bids[5]'],
    ['prosumer_s1[5]', 'emarket[0]', 'em_demand_bids', 'demand_bids[5]'],
    ['emarket[0]', 'prosumer_s1[5]', 'accepted_bids', 'em_accepted_bids','time_shifted=True'],
    ['prosumer_s1[5]', 'monitor', 'p2em','p2em'],

       # -- Ftrading ---------------------------------------------------------------------------
    ['p2ptrading[0]', 'monitor', 'quantity_traded','quantity_traded'],

    # Agent 0 in Ftrading
    ['prosumer_s1[0]', 'p2ptrading[0]', 'p2p_supply_offers', 'supply_offers[0]'],
    ['prosumer_s1[0]', 'p2ptrading[0]', 'p2p_demand_requests', 'demand_requests[0]'],
    ['p2ptrading[0]', 'prosumer_s1[0]', 'transactions', 'p2p_transactions','time_shifted=True'],
    ['prosumer_s1[0]', 'monitor', 'p2p2p','p2p2p'],

    # Agent 1 in Ftrading
    ['prosumer_s1[1]', 'p2ptrading[0]', 'p2p_supply_offers', 'supply_offers[1]'],
    ['prosumer_s1[1]', 'p2ptrading[0]', 'p2p_demand_requests', 'demand_requests[1]'],
    ['p2ptrading[0]', 'prosumer_s1[1]', 'transactions', 'p2p_transactions','time_shifted=True'],
    ['prosumer_s1[1]', 'monitor', 'p2p2p','p2p2p'],

    # Agent 2 in Ftrading
    ['prosumer_s1[2]', 'p2ptrading[0]', 'p2p_supply_offers', 'supply_offers[2]'],
    ['prosumer_s1[2]', 'p2ptrading[0]', 'p2p_demand_requests', 'demand_requests[2]'],
    ['p2ptrading[0]', 'prosumer_s1[2]', 'transactions', 'p2p_transactions','time_shifted=True'],
    ['prosumer_s1[2]', 'monitor', 'p2p2p','p2p2p'],

    # Agent 3 in Ftrading
    ['prosumer_s1[3]', 'p2ptrading[0]', 'p2p_supply_offers', 'supply_offers[3]'],
    ['prosumer_s1[3]', 'p2ptrading[0]', 'p2p_demand_requests', 'demand_requests[3]'],
    ['p2ptrading[0]', 'prosumer_s1[3]', 'transactions', 'p2p_transactions','time_shifted=True'],
    ['prosumer_s1[3]', 'monitor', 'p2p2p','p2p2p'],

    # Agent 4 in Ftrading
    ['prosumer_s1[4]', 'p2ptrading[0]', 'p2p_supply_offers', 'supply_offers[4]'],
    ['prosumer_s1[4]', 'p2ptrading[0]', 'p2p_demand_requests', 'demand_requests[4]'],
    ['p2ptrading[0]', 'prosumer_s1[4]', 'transactions', 'p2p_transactions','time_shifted=True'],
    ['prosumer_s1[4]', 'monitor', 'p2p2p','p2p2p'],

    # Agent 5 in Ftrading
    ['prosumer_s1[5]', 'p2ptrading[0]', 'p2p_supply_offers', 'supply_offers[5]'],
    ['prosumer_s1[5]', 'p2ptrading[0]', 'p2p_demand_requests', 'demand_requests[5]'],
    ['p2ptrading[0]', 'prosumer_s1[5]', 'transactions', 'p2p_transactions','time_shifted=True'],
    ['prosumer_s1[5]', 'monitor', 'p2p2p','p2p2p'],
]

try:
    df=pd.DataFrame(connection, columns=['send','receive','messages','messager','more'])
except ValueError:
    df=pd.DataFrame(connection, columns=['send','receive','messages','messager'])
data=df.to_xml()

with open('../../Cases/GameCase/connection.xml','w') as file:
    file.write(data)
