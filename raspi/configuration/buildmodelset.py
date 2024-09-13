


Battery_initialset = {'initial_soc': 20}
Battery_set = {'max_p': 800, 'min_p': -800, 'max_energy': 800,
            'charge_efficiency': 0.9, 'discharge_efficiency': 0.9,
            'soc_min': 10, 'soc_max': 90, 'flag': 0, 'resolution': 15}  #p in kW
#Set flag as 1 to show fully discharged state; -1 show fully charged,0 show ready to charge and discharge

h2storage_initial = {'initial_soc': 50}
h2_set = {'h2storage_soc_min': 10, 'h2storage_soc_max': 90, 'max_h2': 500, 'min_h2': -500, 'flag': -1, 'capacity':50000}
#max_h2 in kWh; flag as 1 to show fully discharged state; -1 show fully charged,0 show ready to charge and discharge

pv_panel_set ={'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800,
          'Power_output_at_STC': 250}
pv_set={'m_tilt':14,'m_az':180,'cap':500,'output_type':'power'}
# 'NOCT':degree celsius; 'Irradiance_at_NOCT':W/m2 This is the irradiance that falls on the panel under NOCT conditions
# KW. Available in spec sheet of a module
load_set={'houses':1000, 'output_type':'power'}

Wind_set={'p_rated':300, 'u_rated':10.3, 'u_cutin':2.8, 'u_cutout':25, 'cp':0.40, 'diameter':22, 'output_type':'power'}
#  p_rated  # kW power it generates at rated wind speed and above
# u_rated  # m/s #windspeed it generates most power at
#  u_cutin  # m/s #below this wind speed no power generation
# u_cutout  # m/s #above this wind speed no power generation. Blades are pitched
# cp  # coefficient of performance of a turbine. Usually around0.40. Never more than 0.59
# powerout = 0  # output power at wind speed u
fuelcell_set={'eff':0.45}

electrolyser_set={'eff':0.60,'fc_eff':0.45,'resolution':15}

RESULTS_SHOW_TYPE={'write2csv':True, 'dashboard_show':False, 'Finalresults_show':True}
#'write2csv':True/Flause   Write the results to csv file
# #'Realtime_show':True/Flause, show the results in dashboard
# 'Finalresults_show':True/Flause, show the results after finish the simulation

realtimefactor=0
#0 as soon as possible. 1/60 using 1 second simulate 1 mintes
