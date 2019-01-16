import math
import cmath
import numpy as np
import matplotlib.pyplot as plt


PATH = '/Users/Home/Cloud/Cernbox/hgcSensorTesting/Software/python/'
FREQ = 50000


def lcr_open_short_load_cor(z_m, z_open, z_short, z_load, z_std):
    return z_std * ((z_short - z_m)*(z_load - z_open))/((z_m - z_open)*(z_short - z_load)) 

def cap_to_impedance(f, c):
    return (-1)/(2*np.pi*f*c)
    

## Needle data
cell65_50kHz      = np.genfromtxt(PATH + 'logs/HPK1104_7Needles/08_20170331_111358/cv.dat') # 08-> no resistor, decoupling box
cell65_50kHz_open = np.genfromtxt(PATH + 'logs/HPK1104_7Needles/18_20170331_115835/cv.dat') # 18-> no resistor, decoupling box

cv_cell42_22M = np.genfromtxt('/Users/Home/Documents/Code/Works/hgc/hgcSensorAnalysis/basic/sensors/data/hpk1104_cell42/cv_22M/cv.dat', skip_header=1)
cv_cell42_22M_open = np.genfromtxt('/Users/Home/Documents/Code/Works/hgc/hgcSensorAnalysis/basic/sensors/data/hpk1104_cell42/cv_22M_open/cv.dat', skip_header=1)

dat_geometry = np.genfromtxt(PATH + 'config/geometryHPK6inch128.txt', skip_header=1)
dat_stdvalues = []

ref = np.array([val for val in cv_cell42_22M if (val[2] == FREQ)])[1:-1, 8] - np.array([val for val in cv_cell42_22M_open if (val[2] == FREQ)])[1:-1, 8]
res = np.array([val for val in cv_cell42_22M if (val[2] == FREQ)])[1:-1, 3]
volts = np.array([val for val in cv_cell42_22M if (val[2] == FREQ)])[1:-1, 0]

for j in range(len(volts)):
    v = volts[j]
    for line in dat_geometry:
        nr = line[0]
        typ = line[1]

        if typ == 0: # "standard"
            area = 1.08824232749822
        elif typ == 1:
            area = 0.546019079709    # guard ring
        elif typ == 2:
            area = 0.53815632292657  # half cell
        elif typ == 3:
            area = 0.3725866786556   # mouse bite
        elif typ == 4:
            area = 0.93016364267491  # around calibration cell
        elif typ == 5:
            area = 0.145276914154    # calibration cell
        elif typ == 20:
            area = 1.09214686563422  # d = 20um
        elif typ == 40:
            area = 1.08824232749822  # d = 40um
        elif typ == 60:
            area = 1.08437842789322  # d = 60um
        elif typ == 80:
            area = 1.08052139999822  # d = 80um
        else:
            print 'Unknown type.'

        cap_per_cm2 = ref[j] * 1/1.08437842789322

        c = area * cap_per_cm2
        r = res[j]
        x = cap_to_impedance(FREQ, c)

        dat_stdvalues.append([v, nr, typ, area, r, x, c])
        
        
        
hd = 'Standard Values for Load Correction at 50 kHz\n' \
   + 'Extracted from needle measurements of cell 62 at 50 kHz measurement and scaled with area\n' \
   + 'To be used with HPK 6" 128ch sensors as load\n\n' \
   + 'Types:\n' \
   + '  - 0 Full\n' \
   + '  - 1 Guard Ring\n' \
   + '  - 2 Half Cell\n' \
   + '  - 3 Mouse Bite\n' \
   + '  - 4 Outer Calibration Cell\n' \
   + '  - 5 Inner Calibration Cell\n' \
   + '  - 20 Full Cell 20 micron gap\n' \
   + '  - 40 Full Cell 40 micron gap\n' \
   + '  - 60 Full Cell 60 micron gap\n' \
   + '  - 80 Full Cell 80 micron gap\n\n' \
   + 'Voltage [V] Cell Nr. [-] Type [-] Area [cm2] Resistance [Ohm] Reactance [Ohm] Cp [F]\n'

fmt = '%.2f\t%d\t%1d\t%8.5f\t%4.2E\t%8.5E\t%8.5E'
np.savetxt(PATH + 'config/valuesStd50kHz.txt', dat_stdvalues, fmt=fmt, delimiter='\t', newline='\n', header=hd, footer='', comments='# ')
