import math
import cmath
import numpy as np
import matplotlib.pyplot as plt


## Configure
ID = 'HPK1105'
freq = 50000
amp = 0.5


## Definitions
def lcr_open_short_load_cor(z_m, z_open, z_short, z_load, z_std):
    return z_std * ((z_short - z_m)*(z_load - z_open))/((z_m - z_open)*(z_short - z_load)) 

def cap_to_impedance(f, c):
    return (-1)/(2*np.pi*f*c)


## Load correction data
PATH = '/Users/Home/Cloud/Cernbox/hgcSensorTesting/Software/python/'
FILE = '/Users/Home/Cloud/Cernbox/hgcSensorTesting/Software/python/data/%s/cv/cv.dat' % ID
dat_msr = np.genfromtxt(FILE) 

volts = np.genfromtxt(PATH + 'config/voltagesCV.txt')
dat_open = np.genfromtxt(PATH + 'config/valuesOpen50kHz.txt')
dat_short = np.genfromtxt(PATH + 'config/valuesShort50kHz.txt')
dat_load = np.genfromtxt(PATH + 'config/valuesLoad50kHz.txt')
dat_std = np.genfromtxt(PATH + 'config/valuesStd50kHz.txt')

r_short = dat_short[:135, 1]
x_short = dat_short[:135, 2]


x = []
y1 = []
y2 = []
## Corrections
dat_cor = []

for v in volts:
    for ch in [33]:#np.array([val for val in dat_msr if (val[0] == v)])[:135, 2]:
        j = int(ch) - 1
        
        v_msr = np.array([val for val in dat_open if (val[0] == v)])[j, 1]
        r_msr = np.array([val for val in dat_msr if (val[0] == v)])[j, 3]
        x_msr = np.array([val for val in dat_msr if (val[0] == v)])[j, 5]
        c_msr = np.array([val for val in dat_open if (val[0] == v)])[j, 7] * 10**(-12)
        itot_msr = np.array([val for val in dat_open if (val[0] == v)])[j, 8]
        
        r_open = np.array([val for val in dat_open if (val[0] == v)])[j, 3]
        x_open = np.array([val for val in dat_open if (val[0] == v)])[j, 5]
        
        ## If the exact same voltage is available, use it
        if v in dat_std[:, 0]:
            r_load = np.array([val for val in dat_load if (val[0] == v)])[j, 3]
            x_load = np.array([val for val in dat_load if (val[0] == v)])[j, 5]
            r_std = np.array([val for val in dat_std if (val[0] == v)])[j, 4]
            x_std = np.array([val for val in dat_std if (val[0] == v)])[j, 5]
         
        ## Else look for the closest voltage in std that is also in load 
        else:
            idx = np.argmin(np.abs(np.array([val for val in dat_std[:, 0] if val in dat_load[:, 0]]) - v))
            v_closest = np.array([val for val in dat_std[:, 0] if val in dat_load[:, 0]])[idx]
            r_load = np.array([val for val in dat_load if (val[0] == v_closest)])[j, 3]
            x_load = np.array([val for val in dat_load if (val[0] == v_closest)])[j, 5]
            r_std = np.array([val for val in dat_std if (val[0] == v_closest)])[j, 4]
            x_std = np.array([val for val in dat_std if (val[0] == v_closest)])[j, 5]

        r_load = np.array([val for val in dat_load if (val[0] == v_std)])[j, 3]
        x_load = np.array([val for val in dat_load if (val[0] == v_std)])[j, 5]
        r_std = np.array([val for val in dat_std if (val[0] == v_std)])[j, 4]
        x_std = np.array([val for val in dat_std if (val[0] == v_std)])[j, 5]    
        
        z_msr = r_msr + 1j * x_msr
        z_open = r_open + 1j * x_open
        z_short = r_short[j] + 1j * x_short[j]
        z_load = r_load + 1j * x_load
        z_std = r_std + 1j * x_std

        z_cor = lcr_open_short_load_cor(z_msr, z_open, z_short, z_load, z_std)

        r_cor = z_cor.real
        x_cor = z_cor.imag
        c_cor = cap_to_impedance(freq, x_cor)
        
        dat_cor.append([v, v_msr, ch, r_msr, x_msr, c_msr, r_cor, x_cor, c_cor, itot_msr])  

        
        # if j == 131 or j == 32 or j == 100 or j == 101:
        #     print '%d\t%.3E\t%.3E\t%.3E' % (v, r_cor, x_cor, c_cor)
        
        if j == 32:
            x.append(v)
            y1.append(c_cor)
            y2.append((0.9*10**(-31))/(c_cor**2))

plt.plot(x[3:], y1[3:], 'k', marker='o', ls = ':')
plt.plot(x[3:], y2[3:], 'r', marker='s', ls = ':')
plt.show()
    
hd = []
f = open(FILE, 'r')
for line in f:
    if '#' in line:             
        hd.append(line[2:])
hd.pop(-2)
hd.append('Nominal Voltage [V]	 Measured Voltage [V]	Channel [-]	R [kOhm] X [kOhm] C [F] R_cor [kOhm] X_cor [kOhm] C_cor [F]	Total Current [A]\n')
hd = " ".join(hd)

print hd

fmt = '%d\t\t%.2f\t%d\t%.5E\t%.3E\t%.3E\t%.3E\t%.3E\t%.3E\t%.3E'
fn = FILE[:-4] + '_corrected' + FILE[-4:]

np.savetxt(fn, dat_cor, fmt=fmt, delimiter='\t', newline='\n', header=hd, footer='', comments='# ')
    