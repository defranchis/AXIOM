import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator
from matplotlib.cm import coolwarm, ScalarMappable
from matplotlib import gridspec
from matplotlib.pyplot import axhline, subplots, show, hist, figure, setp, colorbar, plot, cm, title, xlabel, ylabel, grid, legend, savefig, axes, pcolormesh, close
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator, MaxNLocator
import matplotlib.colors as colors

from Oxides import Oxide
from Plotter import Plotter

import os
import glob
import numpy as np
import sys



correction = {1e4: [[2.1170495e+02, -3.1941629e+05], [1.4886421, -10.322904 ]], 1e5: [[1.2350204e+01, -3.1948538e+04], [2.0442465, 2.0464124]], 1e6: [[1.6571294e+00, -3.2034364e+03], [4.2284494, 24.491841]]}





if __name__ == '__main__':


    p = Plotter()
    args = sys.argv
    name = args[1]
    length = 2.35
    folder = 'logs/Strip_'+args[2]

    interestingVoltages = [-100, -250, -400] if '120um' in folder else ([-200, -400, -600] if '200um' in folder else [-400, -600, -800])
    interestingFreqs = [1e6]
    o = Oxide(name, length, folder, correction)


    p.plotCV_freq(o)
    p.plotCtime(o, 1e6, interestingVoltages)
    p.plotRV(o)
    p.plotRtime(o, interestingVoltages)

    for d in o.time:
        p.plotIV_Bias(o, d, interestingVoltages)
    for v in interestingVoltages:
        p.plotIV_time(o, o.time, v)

        
    p.plotT_time(o)
    p.plotTRSame_time(o, interestingVoltages)
    p.plotTR(o, interestingVoltages)




