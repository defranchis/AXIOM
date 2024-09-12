# ============================================================================
# File: testMD_fullSensorMeasurements.py
# ------------------------------
#
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       measure voltage, current, total current
#   finish
#
# Status:
#   under debvelopment
#
# ============================================================================
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


plt.style.use('ggplot')

import time, math, os
import logging
import numpy as np
from measurements.measurement import measurement

from devices.ke2410 import * # power supply
from devices.ke6487 import * # picoammeter and votlage source for IV bias of -10 V
from devices.ke7001 import * # switch
from devices.hp4980 import * # switch

import mpld3

## load plotting functions
#from utils.liveplotting import *

from utils.correct_cv import lcr_series_equ, lcr_parallel_equ, lcr_error_cp

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(13,13))
    ax0 = fig.add_subplot(131)
    ax1 = fig.add_subplot(132)
    ax2 = fig.add_subplot(133)


    return fig, ax0, ax1, ax2


def live_plotter(x_vec, y_vec, ax, line, identifier='', yaxis_title='', color='k',pause_time=0.1):
    if line == []:
        #plt.ion()
        ax.clear()
        plt.cla()

        line, = ax.plot(x_vec, y_vec, color[0]+'-o', alpha=0.8)

        ax.set_title(identifier)
        ax.set_ylabel(yaxis_title)
        ax.set_xlabel('bias voltage [V]')
        plt.show()
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()

    line.set_xdata(x_vec)
    line.set_ydata(y_vec)

    ax.set_ylim([np.min(y_vec)-0.005*abs(np.min(y_vec)),np.max(y_vec)+0.005*abs(np.max(y_vec))])
    ax.set_xlim([np.min(x_vec)-0.5,np.max(x_vec)+0.5])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    return line


class testMD_fullStrip(measurement):
    """Measurement of a dummy I-V curve. """

    def initialise(self):

        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running 2 CV scans :)")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        ## KEITHLEY settings
        self.keithley2410_address =  8      # in the SSD lab gpib address of the power supply that does the IV scan
        self.switch_address       = 7       # gpib address of the switch

        ## LCR meter settings
        self.lcr_meter_address = 17         # in the SSD lab this is 9
        #self.cv_res = 1e6                   # cv parallel resistor in [Ohm]
        
        self.lcr_vol = 0.5 #0.501             # ac voltage amplitude in [mV]
        self.lcr_freq = 1e4    # ac voltage frequency in [Hz]
        self.lcr_mode = 'RX'
        self.approx_open_corr = 50e-12


        self.lim_cur_ke2410 = 1E-4          # compliance in [A]
        #self.lim_vol = 10                   # compliance in [V]

        v_min = -20
        v_max = -120
        step = -2
        self.volt_list_CV = [round(v,1) for v in np.arange(v_min, v_max + step, step)]

        self.nSampling_CV = 10
        self.delay_vol_cv = 10     # delay between setting voltage and executing measurement in [s]

        ## initialize the devices

        self.keithley2410 = ke2410(self.keithley2410_address)

        self.switch = ke7001(self.switch_address)
        self.reset_switch()

        ## Set up lcr meter
        self.lcr_meter = hp4980(self.lcr_meter_address)
        self.lcr_meter.reset()
        self.lcr_meter.set_voltage(self.lcr_vol)
        self.lcr_meter.set_mode(self.lcr_mode)
        self.lcr_meter.set_frequency(self.lcr_freq)




    def reset_power_supplies(self):

        ## Reset power supply for CV measurement


        self.keithley2410.ramp_down()
        self.keithley2410.set_output_off()
        self.keithley2410.reset()
        self.keithley2410.set_source('voltage')
        self.keithley2410.set_sense('current')
        self.keithley2410.set_current_limit(self.lim_cur_ke2410)
        self.keithley2410.set_voltage(0)
        self.keithley2410.set_terminal('rear')
        time.sleep(3)
        self.keithley2410.set_output_off()
        time.sleep(1)
        

    def reset_switch(self):

        ## Set up the switch
        self.switch.reset(1)
        self.switch.get_idn()
        self.switch.open_all()
    
    def saveSinglePlot(self, fig, ax, name):
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        #fig.savefig(name, bbox_inches=extent)
        fig.savefig(self.rdir+'/'+name, bbox_inches=extent.expanded(1.2, 1.2))
        return 0
    

    def savePlots(self, dic):
        ### Save and print
        for name,val in dic.items():
            self.print_graph(np.array(val)[:, 1], np.array(val)[:, 7], np.array(val)[:, 7] * 0.01, \
                             'Bias Voltage [V]', 'Parallel Capacitance [F]',  'CV ' + self.id + ' ' +name, fn="cv_{a}_{b}.png".format(a=self.id, b=name))
            self.print_graph(np.array(val)[2:, 1], np.array(val)[2:, 7]**(-2), 0, \
                             'Bias Voltage [V]', '1/C^2 [1/F^2]',  '1/C2 ' + self.id + ' ' + name, fn="1c2v_{a}_{b}.png".format(a=self.id, b=name))
            self.print_graph(np.array(val)[:, 1], np.array(val)[:, 9], np.array(val)[:, 9]*0.01, \
                             'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_total_current_{a}_{b}.png".format(a=self.id, b=name))


    def createHeader(self):
        # CV
        lim_vol  = self.keithley2410.check_voltage_limit()
        lim_cur  = self.keithley2410.check_current_limit()
        lcr_vol  = float(self.lcr_meter.check_voltage())
        lcr_freq = float(self.lcr_meter.check_frequency())

        ## Header
        hdCV = [
            'CV Sweep\n',
            'Measurement Settings:',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % float(lim_cur),
            'LCR measurement voltage:         %8.2E V' % lcr_vol,
            'LCR measurement frequency:       %8.2E Hz' % lcr_freq,
            'Voltage Delay:                   %8.2f s' % self.delay_vol_cv,
            'Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]'
        ]


        return(hdCV)




    def CVpoint(self, biasV): 

        self.keithley2410.set_voltage(biasV)
        time.sleep(self.delay_vol_cv)

        cur_tot = self.keithley2410.read_current()
        vol = self.keithley2410.read_voltage()


        measurements = np.array([self.lcr_meter.execute_measurement() for _ in range(self.nSampling_CV)])
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.nSampling_CV)

        r, x = means
        dr, dx = errs

        z = np.sqrt(r**2 + x**2)
        phi = np.arctan(x/r)
        r_s, c_s, l_s, D = lcr_series_equ(self.lcr_freq, z, phi)
        r_p, c_p, l_p, D = lcr_parallel_equ(self.lcr_freq, z, phi)

        line = [biasV, vol, self.lcr_freq, r_p, dr, x, dx, c_s, c_p, cur_tot]
        
        self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        return (line)
        ## end of CV scan



    def CVscan(self, name, fig, ax0, hdCV, shortGR=False, groundGR=False):

        if shortGR and groundGR:
            raise ValueError('shortGR and groundGR cannot be simultaneously true')

        self.logging.info('\n\nSTARTING CV SCAN...\n\n')
        tag = 'float'
        if shortGR : tag = 'short'
        elif groundGR: tag = 'ground'
        fname_out_CV = '_'.join(['cv', self.id, name]) + '_{}.dat'.format(tag)

        biasVs = []
        Cs_LCR = []
        line = []
        outCV = []  
        if shortGR: color = 'r'
        elif groundGR: color = 'g'
        else: color = 'b'


        self.reset_power_supplies()
        self.reset_switch()

        if shortGR:
            self.switch.close_channel(1)
        elif groundGR:
            self.switch.close_channel(3)

        self.keithley2410.set_output_on()


        # Do CV Scan
        try:            
            self.logging.info("Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]")
            for v in self.volt_list_CV:
                lineCV = self.CVpoint(v)      
                    
                outCV.append(lineCV)
                biasVs.append(lineCV[0])
                Cs_LCR.append(lineCV[8])
                label = 'CV floating GR'
                if shortGR: label = 'CV shorted GR'
                elif groundGR: label = 'CV grounded GR'
                line = live_plotter(biasVs, 1/(np.abs(np.array(Cs_LCR))-self.approx_open_corr)**2, ax0, line, identifier=label, yaxis_title='1/Cs^2 [F^-2]', color=color)                


        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED IN CV SCAN:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        self.reset_power_supplies()
        self.reset_switch()


        self.saveSinglePlot(fig, ax0, tag+"_cv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.save_list(outCV, tag+'_'+fname_out_CV, fmt="%.5E", header="\n".join(hdCV))

        self.logging.info('\n\n CV SCAN FINISHED\n\n')



    def execute(self):

        # Name of files
        name = "Test_name"

        # Create plots
        fig, ax0, ax1, ax2 = init_liveplot()

        ## Print header
        hdCV = self.createHeader()
        for line in hdCV:
            self.logging.info(line)

        self.CVscan(name, fig, ax0, hdCV)
        self.CVscan(name, fig, ax1, hdCV, shortGR=True)
        self.CVscan(name, fig, ax2, hdCV, groundGR=True)


        

    def finalise(self):
        self._finalise()