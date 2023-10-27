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
plt.style.use('ggplot')

import time, math, os
import logging
import numpy as np
from measurements.measurement import measurement

from devices.ke2410 import * # power supply
from devices.ke6487 import * # picoammeter and votlage source for IV bias of -10 V
from devices.ke7001 import * # switch
from devices.hp4980 import * # switch

## load plotting functions
#from utils.liveplotting import *

from utils.correct_cv import lcr_series_equ, lcr_parallel_equ, lcr_error_cp

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(15,5))
    ax0 = fig.add_subplot(131)
    ax1 = fig.add_subplot(132)
    ax2 = fig.add_subplot(133)

    return fig, ax0, ax1, ax2

def mypause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(interval)
            return

def live_plotter(x_vec, y_vec, ax, line, identifier='', yaxis_title='', color='k',pause_time=0.1):
    if line == []:
        #plt.ion()
        line, = ax.plot(x_vec, y_vec, color[0]+'-o', alpha=0.8)

        ax.set_title(identifier)
        #update plot label/title
        ax.set_ylabel(yaxis_title)
        ax.set_xlabel('voltage')
        plt.show()

    line.set_xdata(x_vec)
    line.set_ydata(y_vec)

    # adjust limits if new data goes beyond bounds
    if np.min(y_vec)<=line.axes.get_ylim()[0] or np.max(y_vec)>=line.axes.get_ylim()[1]:
        ax.set_ylim([np.min(y_vec)-np.std(y_vec),np.max(y_vec)+np.std(y_vec)])
    if np.min(x_vec)<=line.axes.get_xlim()[0] or np.max(x_vec)>=line.axes.get_xlim()[1]:
        ax.set_xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    #mypause(pause_time)

    return line


class testMD_simple_CV(measurement):
    """Measurement of a dummy I-V curve. """

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running all 3 measurements of the silicon!")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        ## KEITHLEY settings
        self.keithley2410_address =  4  # in the SSD lab gpib address of the power supply that does the IV scan

        ## LCR meter settings
        self.lcr_meter_address = 17  # in the SSD lab this is 9
        self.lcr_vol = 0.5             # ac voltage amplitude in [mV]
        self.lcr_freq = 2000            # ac voltage frequency in [Hz]
        self.cv_res = 1e6                # cv parallel resistor in [Ohm]

        self.lim_cur_ke2410 = 10e-6  # compliance in [A]
        self.lim_vol = 10             # compliance in [V]

        self.volt_list_cv = [-i*10 for i in range(1,35)]
        self.currents_cv  = [0 for i in self.volt_list_cv]

        self.nSampling_CV =  5

        self.delay_vol_cv = 10     # delay between setting voltage and executing measurement in [s]

        ## initialize the devices
        self.keithley2410 = ke2410(self.keithley2410_address)

        ## Set up lcr meter
        self.lcr_meter = hp4980(self.lcr_meter_address)
        self.lcr_meter.reset()
        self.lcr_meter.set_voltage(self.lcr_vol)
        self.lcr_meter.set_frequency(self.lcr_freq)
        self.lcr_meter.set_mode('RX')

        #self.reset_power_supplies()


    def reset_power_supplies(self):

        ## Reset power supply for CV measurement
        self.keithley2410.ramp_down()
        self.keithley2410.set_output_off()
        self.keithley2410.reset()
        self.keithley2410.set_source('voltage')
        self.keithley2410.set_sense('current')
        self.keithley2410.set_current_limit(self.lim_cur_ke2410)
        self.keithley2410.set_voltage(0)
        self.keithley2410.set_terminal('front')
        # MARC keithley2410.set_interlock_on()
        self.keithley2410.set_output_off()
        time.sleep(1)

    def savePlots(self, dic):
        ### Save and print
        for name,val in dic.items():
            if 'cv' in name:
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 7], np.array(val)[:, 7] * 0.01, \
                                 'Bias Voltage [V]', 'Parallel Capacitance [F]',  'CV ' + self.id + ' ' +name, fn="cv_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[2:, 1], np.array(val)[2:, 7]**(-2), 0, \
                                 'Bias Voltage [V]', '1/C^2 [1/F^2]',  '1/C2 ' + self.id + ' ' + name, fn="1c2v_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 9], np.array(val)[:, 9]*0.01, \
                                 'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_total_current_{a}_{b}.png".format(a=self.id, b=name))

            elif 'iv' in name:
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 2], np.array(val)[:, 3], \
                                 'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array([val for val in val if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 1], \
                                 np.array([val for val in val if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 2], \
                                 np.array([val for val in val if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 3], \
                                 'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_zoom_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 4], np.array(val)[:, 4]*0.01, \
                                 'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_total_current_{a}_{b}.png".format(a=self.id, b=name))

    def doCVScan(self, ax, name=''):  ## don't really know how best to do this ... to be teasted on the setup

        self.keithley2410.set_output_on()

        ## Check settings
        lim_vol  = self.keithley2410.check_voltage_limit()
        lim_cur  = self.keithley2410.check_current_limit()
        lcr_vol  = float(self.lcr_meter.check_voltage())
        lcr_freq = float(self.lcr_meter.check_frequency())

        ## Header
        hd = [
            'Single IV\n',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % float(lim_cur),
            'LCR measurement voltage:         %8.2E V' % lcr_vol,
            'LCR measurement frequency:       %8.2E Hz' % lcr_freq,
            'Voltage Delay:                   %8.2f s' % self.delay_vol_cv,
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]'
        ]

        ## Print Info
        for line in hd[1:-2]:
            self.logging.info(line)
        self.logging.info("\t")
        self.logging.info("\t")
        self.logging.info(hd[-1])
        self.logging.info("-" * int(1.2 * len(hd[-1])))

        ## Prepare
        out = []

        ## for plotting
        tmp_id_title = 'CV '+ name+ ': ' + self.id.replace('_m',' -').replace('_p',' +').replace('_',' ')
        tmp_id_y     = 'capacitance'
        color = 'b' if  'MOShalf' in name else 'r' if 'MOS2000' in name else 'c'
        tmp_x, tmp_y = [], []
        tmp_yI = []
        line0 = []
        line1 = []
        line2 = []

        c_baseline = 0. ## this will be the baseline of the first 10 voltages
        rolling_avg = []

        try:

            ## Loop over voltages
            for iv, v in enumerate(self.volt_list_cv):
                self.keithley2410.ramp_voltage(v)
                time.sleep(self.delay_vol_cv)

                cur_tot = sum([self.keithley2410.read_current() for i in range(10)])/10.
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

                line = [v, vol, self.lcr_freq, r, dr, x, dx, c_s, c_p, cur_tot]
                out.append(line)
                #self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(c_s)

                tmp_yI.append(cur_tot)

                ## update the live plotting
                line0 = live_plotter(tmp_x, tmp_y, ax[0], line0, identifier=tmp_id_title, yaxis_title=tmp_id_y, color=color)
                line1 = live_plotter(tmp_x, tmp_yI, ax[1], line1, identifier=tmp_id_title, yaxis_title="Current", color=color)
                line2 = live_plotter(tmp_x, 1./np.array(tmp_y)**2, ax[2], line2, identifier=tmp_id_title, yaxis_title="1/C$^2$", color=color)

                # if c_s > 0.9*reference_capacitance and not self.is_preirradiation: ## start checking the flattening once the c_s goes above 120% of the baseline
                #     ## let's abort once the current rolling average is between the min and max of the last 10 values
                #     print('this is the rms of the last 10', rms)
                #     if 0.985*rms < c_s < 1.015*rms:
                #         self.logging.info('it looks like the plateau is reached... ending measurement!')
                #         if plateauVoltage > 0: plateauVoltage = v
                #         if not self.is_preirradiation and v < 1.2*plateauVoltage:
                #             break
                #         else:
                #             self.logging.info('going on because this is a preirradiated sample or we want to go the extra mile...')

        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        ## Save and print
        fname_out = '_'.join(['cv', self.id, name]) + '.dat'
        self.logging.info("\n")
        self.save_list(out, fname_out, fmt="%.5E", header="\n".join(hd))

        return out

    def execute(self):

        ## reset all the stuff first
        ## =========================================
        self.reset_power_supplies()

        fig, ax0, ax1,ax2 = init_liveplot()

        plots = {}

        ## starting the measurements
        plots_cv_diode = self.doCVScan([ax0,ax1,ax2], name='Diode')
        plots["cv_diode"] = plots_cv_diode
        
        ## Close connections
        self.reset_power_supplies()
        
        # plots_cv_mos2000 =self.doCVScan(ax1, name='MOS2000')
        # plots["cv_mos2000"] = plots_cv_mos2000
        
        # ## Close connections
        # self.reset_power_supplies()
        
        # plots_iv_gcd = self.doIVScan(9, ax2, name='GCD')
        # plots["iv_gcd"] = plots_iv_gcd
        
        # ## Close connections
        # self.reset_power_supplies()

        #except BaseException as e:
        #print('EXCEPTION RAISED:', e)
        #self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
        #self.logging.error(e)

        self.savePlots(plots)


    def finalise(self):
        self._finalise()

