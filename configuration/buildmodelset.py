# [Manuel] FROM Balassis thesis:
# The buildmodelset.py file holds the parameters for each simulator. It is imported into the Main file and used to
# instantiate the models with the appropriate setup. This file allows for the specification of various parameters related
# to physical energy assets, like the initial SoC of batteries or the rated power of wind turbines. Additionally, economic
# parameters, such as the marginal cost or benefit of each asset in agents’ portfolios, can also be defined among the
# available parameters.

resolution=15
Battery_initialset = {'initial_soc': 20}
Battery_set = {'max_p': 800, 'min_p': -800, 'max_energy': 800,
            'charge_efficiency': 0.9, 'discharge_efficiency': 0.9,
            'soc_min': 10, 'soc_max': 90, 'flag': 0,'resolution':resolution}  #p in kW
#Set flag as 1 to show fully discharged state; -1 show fully charged,0 show ready to charge and discharge

h2storage_initial = {'initial_soc': 50}
ttrailers_initial = {'initial_soc': 20}
h2_set = {'h2storage_soc_min': 10, 'h2storage_soc_max': 90, 'max_h2': 0.3,
          'min_h2': -0.3, 'flag': 0, 'capacity':30, 'eff': 0.94, 'resolution':resolution}
h2trailer_set = {'h2storage_soc_min': 10, 'h2storage_soc_max': 90, 'max_h2': 0.3,
          'min_h2': -0.3, 'flag': 0, 'capacity':3000, 'eff': 0.94, 'resolution':resolution}
# max_h2 min_h2 in m^3/min;
# flag as 1 to show fully discharged state; -1 show fully charged,0 show ready to charge and discharge
# approx efficiency of compressed hydrogen storage tanks. Roundtrip efficiency
# Capacity is max m3 of hydrogen that it can contain

pv_panel_set ={'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800,
          'Power_output_at_STC': 250,'peak_power':600}
pv_set={'m_tilt':14,'m_az':180,'cap':500,'output_type':'power'}
# 'NOCT':degree celsius; 'Irradiance_at_NOCT':W/m2 This is the irradiance that falls on the panel under NOCT conditions
# KW. Available in spec sheet of a module
load_set={'houses':1000, 'output_type':'power'}

Wind_set={'p_rated':300, 'u_rated':10.3, 'u_cutin':2.8, 'u_cutout':25, 'cp':0.40, 'diameter':22, 'output_type':'power'}
Wind_on_set={'p_rated':300, 'u_rated':10.3, 'u_cutin':2.8, 'u_cutout':25, 'cp':0.40, 'diameter':22, 'output_type':'power'}
Wind_off_set={'p_rated':200, 'u_rated':7.5, 'u_cutin':2.8, 'u_cutout':15, 'cp':0.40, 'diameter':15, 'output_type':'power'}
#  p_rated  # kW power it generates at rated wind speed and above
# u_rated  # m/s #windspeed it generates most power at
#  u_cutin  # m/s #below this wind speed no power generation
# u_cutout  # m/s #above this wind speed no power generation. Blades are pitched
# cp  # coefficient of performance of a turbine. Usually around0.40. Never more than 0.59
# powerout = 0  # output power at wind speed u
fuelcell_set={'eff':0.45, 'term_eff': 0.2,'max_flow':100, 'min_flow':0,'resolution':resolution}

electrolyser_set={'eff':0.60,'resolution':resolution, 'term_eff': 0.2,'rated_power':2.3,'ramp_rate':1.5}
# term_eff:  percentage of power transformed in effective heat

RESULTS_SHOW_TYPE={'write2csv':True, 'dashboard_show':False, 'Finalresults_show':True,'database':False,'mqtt':False}
#'write2csv':True/Flause   Write the results to csv file
# #'Realtime_show':True/Flause, show the results in dashboard
# 'Finalresults_show':True/Flause, show the results after finish the simulation

enetwork_set={'max_congestion': 1000, 'p_loss_m': 0.56, 'length': 300}

h2network_set={'max_congestion': 700, 'V': 0.0314, 'leakage': 0.03, 'ro': 0.0899}
# max_congestion: max internal pressure bar
# leakage: % of internal flow loss
# ro: gas density kg/m^2 at STP

heatnetwork_set = {'max_temperature': 300 + 275.15, 'insulation': 0.02, 'ext_temp': 25 + 275.15, 'therm_cond': 0.05,
                'length': 100, 'diameter': 0.3, 'density': 1000,  'c': 4.18}
# max_temperature : max_temperature allowed before congestion # K
# insulation:  insulation layer diameter #m
# ext_temp: external temperature # K
# therm_cond: thermal conductivity # W/(m·K)
# leght: lenght of pipeline # m
# diameter: pipe diameter # m
# density: water density # kg/m^3
# c : Thermal capacity of the medium #kJ/(kg·K)

h2demand_r_set={'houses':0.5}
h2demand_fs_set={'tanks':1}
h2demand_ev_set={'cars':1}
h2product_set={'houses':1}


heatstorage_set = {'soc_init': 20, 'max_temperature': 300 + 275.15, 'min_temperature': 25+275.15, 'insulation': 0.20,
                'ext_temp': 25 + 275.15, 'therm_cond': 0.03,
                'length': 2.5, 'diameter': 1.5, 'density': 1000,  'c': 4.18, 'eff': 0.85, 'max_q': 300, 'min_q': -300}
# max_temperature : max_temperature allowed before soc max # K
# min_temperature : max_temperature allowed before soc min # K
# insulation:  insulation layer diameter #m
# ext_temp: external temperature # K
# therm_cond: thermal conductivity # W/(m·K)
# leght: lenght of pipeline # m
# diameter: pipe diameter # m
# density: water density # kg/m^3
# c: Thermal capacity of the medium #kJ/(kg·K)
# eff: charge/discharge efficiency

# Seasonal storage
heatstorage_s_set = {'soc_init': 80, 'max_temperature': 300 + 275.15, 'min_temperature': 25+275.15, 'insulation': 0.20,
                'ext_temp': 25 + 275.15, 'therm_cond': 0.03,
                'length': 10, 'diameter': 2, 'density': 1000,  'c': 4.18, 'eff': 0.85, 'max_q': 300, 'min_q': -300}
# Daily storage
heatstorage_d_set = {'soc_init': 80, 'max_temperature': 300 + 275.15, 'min_temperature': 25+275.15, 'insulation': 0.20,
                'ext_temp': 25 + 275.15, 'therm_cond': 0.03,
                'length': 0.5, 'diameter': 1, 'density': 1000,  'c': 4.18, 'eff': 0.85, 'max_q': 300, 'min_q': -300}

heatdemand_i_set={'factories':1}
heatdemand_r_set={'houses':1}
heatproduct_set={'utilities':1}

hp_params = {'hp_model': 'Air_8kW',
             'heat_source': 'air',
             'cons_T': 35,
             'heat_source_T': 4,
             'T_amb': 25,
             'calc_mode': 'fast',
             'number': 15}

eboiler_set = { 'capacity':30, 'min_load':5, 'max_load':10, 'standby_loss':0.2,
                'efficiency':0.8,'resolution':resolution}

realtimefactor=0
#0 as soon as possible. 1/60 using 1 second simulate 1 mintes

metrics = {'prosumer_s1_0': {'MC': [0.07, 0.10], 'MB': [0.12],'MO': [0.05, 0.25], 'MR': [0.40]},
           'prosumer_s1_1': {'MC': [0.27], 'MB': [0.20], 'MO': [0], 'MR': [0.33]},
           'prosumer_s1_2': {'MC': [0.33, 0.07], 'MB': [0.18], 'MO': [0.09, 0.22], 'MR': [0.15]},
           'prosumer_s1_3': {'MC': [0], 'MB': [0.50], 'MO': [0], 'MR': [0.50]},
           'prosumer_s1_4': {'MC': [0.10,0.37], 'MB': [0.44], 'MO': [0.01, 0.20], 'MR': [0.20]},
           'prosumer_s1_5': {'MC': [0.12], 'MB': [0.28], 'MO': [0.17], 'MR': [0.19]},
}

