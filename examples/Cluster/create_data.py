#!/usr/bin/env python3
"""
Create a synthetic clear-sky summer day dataset that matches:
- Date range: 2012-06-21 00:00:00 to 2012-06-21 23:45:00
- Timestep: 15 minutes
- Columns: Time,G_Gh,G_Dh,G_Bn,Ta,hs,FF,Az
- Shape: Gaussian-like irradiance peaking at solar noon, 20% diffuse / 80% beam-normal
- Constant Ta=25, FF=2.0; smooth hs and az similar to the sample
"""

import math
from datetime import datetime, timedelta

def generate_rows():
    start = datetime(2012, 6, 21, 0, 0, 0)
    end   = datetime(2012, 6, 21, 23, 45, 0)
    step  = timedelta(minutes=15)

    GHI_peak = 1000.0   # W/m^2 at noon (clear-sky-ish)
    sigma_h  = 2.5      # hours, width of Gaussian "bell"
    day_start, day_end = 6, 18

    t = start
    while t <= end:
        h = t.hour + t.minute/60.0 + t.second/3600.0

        # Gaussian GHI centered at 12:00, zero at night
        if day_start <= h <= day_end:
            f = math.exp(-((h - 12.0)**2) / (2.0 * sigma_h**2))
            G_Gh = GHI_peak * f
        else:
            G_Gh = 0.0

        # Clear-sky split like the sample
        G_Dh = 0.2 * G_Gh
        G_Bn = 0.8 * G_Gh

        # Constant air temp and wind
        Ta = 25.0
        FF = 2.0

        # hs: cosine day-arc (max 70° at noon, -70° at sunrise/sunset), taper to -90° overnight
        if 6 <= h <= 18:
            hs = 70.0 * math.cos(math.pi * (h - 12.0) / 6.0)
        elif h < 6:
            hs = -90.0 + (h / 6.0) * 20.0
        else:
            hs = -70.0 - ((h - 18.0) / 6.0) * 20.0

        # Azimuth: -180° at 00:00, 0° at noon, +90° at 18:00, smoothly sweeping
        Az = -180.0 + 360.0 * (h / 24.0)

        yield f'{t:%Y-%m-%d %H:%M:%S},{G_Gh:.2f},{G_Dh:.2f},{G_Bn:.2f},{Ta:.1f},{hs:.2f},{FF:.1f},{Az:.2f}'
        t += step

def write_file(path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('Solar_data\n')
        f.write('Time,G_Gh,G_Dh,G_Bn,Ta,hs,FF,Az\n')
        for line in generate_rows():
            f.write(line + '\n')

if __name__ == "__main__":
    write_file("examples/Cluster/pv_summer-15min.txt")
