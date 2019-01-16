import math
from cmath import *
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

## Configure
ID = 'HPK_6in_256_5002'
FREQ = 50000
AMP = 0.5

PATH = '/Users/Home/Cloud/Cernbox/hgcSensorTesting/Results/'
FILE = PATH + '%s/%s_CV.txt' % (ID, ID)

COR_OPEN = PATH + 'HPK_6in_256_Open/HPK_6in_256_Open_CV.txt'
COR_SHORT = PATH + 'HPK_6in_256_Short/HPK_6in_256_Short_CV.txt'
COR_LOAD = PATH + 'config/valuesLoad50kHz.txt'
COR_STD = PATH + 'config/valuesStd50kHz.txt'




## Definitions
def lcr_open_cor(c_x, c_open):
    return c_x - c_open


def lcr_open_short_cor(z_x, z_open, z_short):
    return (z_x-z_short) / (1 - (z_x-z_short) * (1/z_open))


def lcr_open_short_load_cor(z_m, z_open, z_short, z_load, z_std):
    return z_std * ((z_short - z_m)*(z_load - z_open))/((z_m - z_open)*(z_short - z_load)) 


def lcr_parallel_equ(f, z, phi):
    y = 1/z
    g_p = y * np.cos(phi)
    b_p = y * np.sin(phi)
    r_p = 1/g_p
    c_p = -b_p / (2 * np.pi * f)
    l_p = 1 / (2 * np.pi * f * b_p)  * (-1)
    D = g_p/b_p

    return r_p, c_p, l_p, D


## Load data
dat_msr = np.genfromtxt(FILE)
dat_open = np.genfromtxt(COR_OPEN)
dat_short = np.genfromtxt(COR_SHORT)
dat_open2 = np.genfromtxt('/Users/Home/Cloud/Cernbox/hgcSensorTesting/Data/SwitchCardMatrixTests/Full matrix_Custom0_noR579/Full matrix_Custom0_noR579_CV.txt')

out = []
volts = []
for line in dat_msr:
    v = line[0]
    if v in volts:
        pass
    else:
        volts.append(v)


#Voltage	#Channel	#Cp  #Error  #Tot. curr.	#Act. vlt.	#Time  	#Temp	#Hum.	#Cs  #Error #Impedance 	#Error #Phase #Error #Cp uncorr.	#Cs uncorr.

# for volt in volts:
#     tmp_msr = np.array([val for val in dat_msr if (val[0] == volt)])
#     tmp_open = np.array([val for val in dat_open2 if (val[0] == volt)])
#
#     r_load = np.array([val for val in tmp_msr if (val[1] == 244)])[0, 11]
#     phi_load = np.array([val for val in tmp_msr if (val[1] == 244)])[0, 13]
#
#     z_load = rect(r_load, phi_load)
#     z_std = rect(94550, -89.975*2*np.pi/360)
#
#     for line in tmp_msr:
#         v = line[0]
#         ch = line[1]
#         v_msr = line[5]
#         temp = line[7]
#         hum = line[8]
#         r = line[11]
#         r_err = line[12]
#         phi = line[13]
#         phi_err = line[14]
#         tot_curr = line[4]
#
#         z = rect(r, phi)
#         cp = lcr_parallel_equ(FREQ, abs(z), phase(z))[1] * 10**12
#
#         r_open = np.array([val for val in tmp_open if (val[1] == ch)])[0, 11]
#         phi_open = np.array([val for val in tmp_open if (val[1] == ch)])[0, 13]
#         z_open = rect(r_open, phi_open)
#
#         r_short = np.array([val for val in dat_short if (val[1] == ch)])[0, 11]
#         phi_short = np.array([val for val in dat_short if (val[1] == ch)])[0, 13]
#         z_short = rect(r_short, phi_short)
#
#         z_scor = lcr_open_short_cor(z, z_open, z_short)
#         cp_scor = lcr_parallel_equ(FREQ, abs(z_scor), phase(z_scor))[1] * 10**12
#
#         z_lcor = lcr_open_short_load_cor(z, z_open, z_short, z_load, z_std)
#         cp_lcor = lcr_parallel_equ(FREQ, abs(z_lcor), phase(z_lcor))[1] * 10**12
#
#         out.append([v, ch, cp_lcor, tot_curr, v_msr, temp, hum])
#

k = 0 
col = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5']
for voltage in [25, 50, 70, 100, 120, 150]:
    x = np.array([10.6, 16.4, 23.14, 33.65, 56.06, 68.66, 103.91, 223.55])
    y = []
    for i in [241, 242, 243, 244, 245, 246, 247, 248]:
        y.append(np.array([val for val in dat_msr if (val[0] == voltage and val[1] == i)])[0, 15])
        
    yo = []
    for i in [241, 242, 243, 244, 245, 246, 247, 248]:
        yo.append(np.array([val for val in dat_open if (val[0] == voltage and val[1] == i)])[0, 15])
    
    ys = []
    for i in [241, 242, 243, 244, 245, 246, 247, 248]:
        ys.append(np.array([val for val in dat_short if (val[1] == i)])[0, 15])
        
    plt.plot(x, y, col[k], label='data') 
    plt.plot(x, yo, 'g', label='open') 
    plt.plot(x, ys, 'b', label='short') 
    
    k += 1
    
def func(x, a, b):
    return 1/(1/x + 1/a) + b
    
popt, pcov = opt.curve_fit(func, x, yo)
plt.plot(x, func(x, popt[0], popt[1]), 'r-', label='fit')

print popt
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()