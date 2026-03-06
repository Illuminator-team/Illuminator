from illuminator.builder import ModelConstructor
import numpy as np
import datetime

class EMSController(ModelConstructor):
    """
    Simple Grid-Aware Energy Management System Controller
    
    Design principle: 
    - Straightforward on/off logic (no prediction)
    - Electrolyzer pulls from GRID (not battery)
    - Fuel cell backup when both grid and battery stressed
    - All parameters tunable for plug-and-play
    """
    
    parameters = {
        # Time settings
        'start_time': '2024-04-01 00:00:00',
        
        # Battery SOC limits (%)
        'soc_min': 20,
        'soc_max': 80,
        
        # Electrolyzer control
        'el_start_soc': 80,         # Battery SOC to allow EL start (%)
        'el_stop_soc': 50,          # Battery SOC to stop EL (%)
        'el_start_hour': 6,         # Earliest hour to start EL
        'el_stop_hour': 13,         # Latest hour to start EL (stop accepting new starts after this)
        'electrolzer_power': 152,   # EL power draw from grid (kW)
        
        # Fuel cell control
        'fc_start_soc': 20,         # Battery SOC to start FC (usually soc_min) (%)
        'fc_threshold_deficit': 60.8,  # Minimum deficit (load-pv) to activate FC (kW)
        
        # H2 storage
        'h2_soc_min': 6,
        'h2_soc_max': 100,
        
        # Grid limits (plug-and-play)
        'grid_import_limit': 250,   # Transformer import limit (kW) - MAIN PARAMETER
        'grid_congestion_threshold': 0.85,  # Start restricting EL at 85% of limit
        
        # Season dates
        'summer_start_month': 4,    # April
        'summer_start_day': 1,
        'summer_end_month': 10,     # October
        'summer_end_day': 14,
    }
    
    inputs = {
        'pv_signal': 0,
        'load_signal': 0,
        'soc': 50,
        'h2_soc': 50,
        'grid_flow': 0,             # Current grid import flow (positive = import)
    }
    
    outputs = {
        'run_electrolyser': 0,      # 1 = EL running, pulls from grid
        'run_fuelcell': 0,          # 1 = FC running, supplies battery
        'compressor_on': 0,
        'storage_flow': 0,          # 1 = store H2, -1 = withdraw H2, 0 = idle
    }
    
    states = {
        'el_state': 0,              # 0 = off, 1 = on
        'fc_state': 0,              # 0 = off, 1 = on
        'el_daily_flag': False,     # Prevents multiple starts per day
        'production_rate': 0,       # EL scaling factor (0.6-1.0)
    }

    time_step_size = 1  
    time = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        # Time
        self.start_time = self._model.parameters.get('start_time')
        
        # Battery
        self.soc_min = self._model.parameters.get('soc_min')
        self.soc_max = self._model.parameters.get('soc_max')
        
        # Electrolyzer
        self.el_start_soc = self._model.parameters.get('el_start_soc')
        self.el_stop_soc = self._model.parameters.get('el_stop_soc')
        self.el_start_hour = self._model.parameters.get('el_start_hour')
        self.el_stop_hour = self._model.parameters.get('el_stop_hour')
        self.electrolzer_power = self._model.parameters.get('electrolzer_power')
        
        # Fuel cell
        self.fc_start_soc = self._model.parameters.get('fc_start_soc')
        self.fc_threshold_deficit = self._model.parameters.get('fc_threshold_deficit')
        
        # H2 storage
        self.h2_soc_min = self._model.parameters.get('h2_soc_min')
        self.h2_soc_max = self._model.parameters.get('h2_soc_max')
        
        # Grid
        self.grid_import_limit = self._model.parameters.get('grid_import_limit')
        self.grid_congestion_threshold = self._model.parameters.get('grid_congestion_threshold')
        
        # Season
        self.summer_start_month = self._model.parameters.get('summer_start_month')
        self.summer_start_day = self._model.parameters.get('summer_start_day')
        self.summer_end_month = self._model.parameters.get('summer_end_month')
        self.summer_end_day = self._model.parameters.get('summer_end_day')
        
        # States
        self.el_state = self._model.states.get('el_state')
        self.fc_state = self._model.states.get('fc_state')
        self.el_daily_flag = self._model.states.get('el_daily_flag')
        self.production_rate = self._model.states.get('production_rate')


    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        """
        Simple control logic:
        
        ELECTROLYZER (Summer only):
        - Start: SOC >= 80% AND Hour 6-13 AND PV > Load AND H2 not full AND not run today
        - Stop: SOC <= 50% OR H2 full OR Grid congested (>85%)
        - Pulls from GRID (not battery)
        
        FUEL CELL (Winter + Summer emergency):
        - Start: SOC <= 20% AND Deficit >= 60.8 kW AND H2 available
        - Stop: SOC >= 82% OR H2 depleted OR Deficit resolved
        - Supplies to BATTERY
        """
        
        input_data = self.unpack_inputs(inputs)
        pv = input_data['pv_signal']
        load = input_data['load_signal']
        soc = input_data['soc']
        h2_soc = input_data['h2_soc']
        grid_flow = input_data['grid_flow']  # Positive = import

        # Parse time
        start_time = datetime.datetime.strptime(
            inputs.get('start_time', self._model.parameters['start_time']), 
            "%Y-%m-%d %H:%M:%S"
        )
        now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
        hour = now.hour
        today_date = now.date()

        # Determine season
        summer_start = datetime.date(today_date.year, self.summer_start_month, self.summer_start_day)
        summer_end = datetime.date(today_date.year, self.summer_end_month, self.summer_end_day)
        is_summer = summer_start <= today_date <= summer_end
        
        # Calculate grid utilization
        grid_utilization = abs(grid_flow) / self.grid_import_limit
        grid_congested = grid_utilization > self.grid_congestion_threshold
        
        # Calculate deficits
        pv_surplus = pv - load  # Positive = surplus PV
        grid_deficit = load - pv  # Positive = need from grid/battery

        print(f"[{now}] Season: {'Summer' if is_summer else 'Winter'} | "
              f"Hour: {hour:02d} | "
              f"Grid: {grid_flow:.1f}/{self.grid_import_limit} kW ({grid_utilization*100:.0f}%) | "
              f"PV-Load: {pv_surplus:+.1f} kW | "
              f"SOC: {soc:.1f}% | H2: {h2_soc:.1f}%")

        # Reset daily flag at midnight
        today_dayofyear = now.timetuple().tm_yday
        if not hasattr(self, 'last_day') or self.last_day != today_dayofyear:
            self.last_day = today_dayofyear
            self.el_daily_flag = False

        # Initialize outputs
        run_el = 0
        run_fc = 0
        storage_flow = 0
        compressor_on = 0
        self.production_rate = 0

        # ====================================================================
        # ELECTROLYZER CONTROL (Summer only, pulls from GRID)
        # ====================================================================
        if is_summer:
            
            if self.el_state == 0:
                # Try to START electrolyzer
                can_start = (
                    soc >= self.el_start_soc and              # Battery must be high
                    hour >= self.el_start_hour and           # After 6 AM
                    hour < self.el_stop_hour and             # Before 1 PM (stop new starts)
                    pv_surplus > 0 and                       # Surplus PV available
                    h2_soc < self.h2_soc_max and             # H2 tank not full
                    not self.el_daily_flag and               # Not already run today
                    not grid_congested                       # Grid not congested
                )
                
                if can_start:
                    self.el_state = 1
                    self.el_daily_flag = True
                    print(f"[{now}] ✅ EL START: SOC {soc:.1f}%, Surplus {pv_surplus:.1f} kW, Grid OK ({grid_utilization*100:.0f}%)")
                else:
                    self.el_state = 0
            
            elif self.el_state == 1:
                # Check if should STOP electrolyzer
                should_stop = (
                    soc <= self.el_stop_soc or              # Battery dropped too low
                    h2_soc >= self.h2_soc_max or            # H2 tank full
                    grid_congested                          # Grid became congested
                )
                
                if should_stop:
                    self.el_state = 0
                    reason = []
                    if soc <= self.el_stop_soc:
                        reason.append(f"SOC low ({soc:.1f}%)")
                    if h2_soc >= self.h2_soc_max:
                        reason.append(f"H2 full ({h2_soc:.1f}%)")
                    if grid_congested:
                        reason.append(f"Grid congested ({grid_utilization*100:.0f}%)")
                    print(f"[{now}] 🛑 EL STOP: {', '.join(reason)}")
                else:
                    self.el_state = 1

            # Set EL outputs
            if self.el_state == 1:
                run_el = 1
                compressor_on = 1
                storage_flow = 1
                # Production rate scales with battery SOC
                if soc < 80:
                    self.production_rate = 0.6
                elif soc <= 90:
                    self.production_rate = 0.6 + (soc - 80) / 100 * 4
                else:
                    self.production_rate = 1.0
            else:
                run_el = 0
                compressor_on = 0

        else:  # Winter
            run_el = 0
            compressor_on = 0

        # ====================================================================
        # FUEL CELL CONTROL (Emergency backup, supplies to BATTERY)
        # ====================================================================
        
        if self.fc_state == 0:
            # Try to START fuel cell
            can_start = (
                soc <= self.fc_start_soc and              # Battery critical (20%)
                grid_deficit >= self.fc_threshold_deficit and  # Large deficit (>60.8 kW)
                h2_soc >= self.h2_soc_min                 # H2 available
            )
            
            if can_start:
                self.fc_state = 1
                print(f"[{now}] 🔥 FC START: SOC {soc:.1f}%, Deficit {grid_deficit:.1f} kW")
            else:
                self.fc_state = 0
        
        elif self.fc_state == 1:
            # Check if should STOP fuel cell
            should_stop = (
                soc >= 82 or                            # Battery recovered
                h2_soc < self.h2_soc_min or             # H2 depleted
                grid_deficit < self.fc_threshold_deficit * 0.8  # Deficit resolved
            )
            
            if should_stop:
                self.fc_state = 0
                reason = []
                if soc >= 82:
                    reason.append(f"SOC recovered ({soc:.1f}%)")
                if h2_soc < self.h2_soc_min:
                    reason.append(f"H2 low ({h2_soc:.1f}%)")
                if grid_deficit < self.fc_threshold_deficit * 0.8:
                    reason.append(f"Deficit resolved ({grid_deficit:.1f} kW)")
                print(f"[{now}] ❄️  FC STOP: {', '.join(reason)}")
            else:
                self.fc_state = 1

        # Set FC outputs
        if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
            run_fc = 1
            storage_flow = -1
        else:
            run_fc = 0

        # ====================================================================
        # SET OUTPUTS AND STATES
        # ====================================================================
        
        self.set_outputs({
            'run_electrolyser': run_el,
            'run_fuelcell': run_fc,
            'compressor_on': compressor_on,
            'storage_flow': storage_flow
        })

        self.set_states({
            'el_state': self.el_state,
            'fc_state': self.fc_state,
            'el_daily_flag': self.el_daily_flag,
            'production_rate': self.production_rate
        })

        return time + self.time_step_size