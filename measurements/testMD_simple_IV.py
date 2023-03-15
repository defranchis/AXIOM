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


class testMD_simple_IV(measurement):
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

        self.lim_cur_ke2410 = 10e-6  # compliance in [A]
        self.lim_cur_ke6487 = 10e-6    # compliance in [A] for the GCD, this should be 10 nA

        self.volt_list_iv = [-i*10 for i in range(1,80)]
        self.currents_iv  = [0 for i in self.volt_list_iv]

        self.nSampling_IV = 30

        self.delay_vol_iv = 5.0     # delay between setting voltage and executing measurement in [s]

        ## initialize the devices
        self.keithley2410 = ke2410(self.keithley2410_address)

        ## Set up volt meter
        self.keithley6487_address = 22
        self.keithley6487 = ke6487(self.keithley6487_address)

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

        #self.keithley6487.ramp_down()
        self.keithley6487.reset()
        self.keithley6487.setup_ammeter()
        self.keithley6487.set_nplc(2)
        self.keithley6487.set_range(self.lim_cur_ke6487)        

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
                
## end of CV scan

    def doIVScan(self, ax, name=''):

        self.keithley2410.set_output_on()

        ## Check settings
        ke6487_lim_vol = -999. #self.keithley6487.check_voltage_limit()
        ke6487_lim_cur = self.lim_cur_ke6487 ## hopefully keithley6487.check_current_limit() #self.keithley6487.check_current_limit()

        ## Check settings
        ke2410_lim_vol  = self.keithley2410.check_voltage_limit()
        ke2410_lim_cur  = self.keithley2410.check_current_limit()

        ## Header
        hd = [
            'Single IV\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.delay_vol_iv,
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
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
        tmp_id_title = 'IV '+ name+ ': ' + self.id.replace('_m',' -').replace('_p', ' +').replace('_',' ')
        tmp_id_y     = 'current'
        color = 'g'
        tmp_x, tmp_y = [], []
        line0 = []

        ## bias the ke6487 to -10 V
        
        ## now new!! self.keithley6487.ramp_voltage(-1*self.gcd_diode_bias)
        ## now new!! time.sleep(self.delay_vol_iv)

        fname_out = '_'.join(['iv', self.id, name]) + '.dat'
        i_baseline = 0. ## this will be the baseline of the first 10 voltages
        stddev, spread = 0., 0.

        try:
            ## Loop over voltages
            for iv,v in enumerate(self.volt_list_iv):
                self.keithley2410.ramp_voltage(v)
                time.sleep(self.delay_vol_iv)

                cur_tot = self.keithley2410.read_current()
                vol = self.keithley2410.read_voltage()

                measurements = np.array([self.keithley6487.read_current() for _ in range(self.nSampling_IV)])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)/math.sqrt(self.nSampling_IV)

                i = means
                di = errs

                line = [v, vol, i, di, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(means)

                ## update the live plotting
                line0 = live_plotter(tmp_x, tmp_y, ax, line0, identifier=tmp_id_title, yaxis_title=tmp_id_y, color='g')
                if i > self.lim_cur_ke6487:
                    self.logging.info('reached compliance in the keithley6487')
                    self.reset_power_supplies()
                    break


        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, fname_out, fmt="%.5E", header="\n".join(hd))
        
        return out


    def execute(self):

        ## reset all the stuff first
        ## =========================================
        self.reset_power_supplies()

        fig, ax0, ax1,ax2 = init_liveplot()

        plots = {}

        plots_iv_diode = self.doIVScan(ax2, name='diode')
        plots["iv_diode"] = plots_iv_diode
        
        ## Close connections
        self.reset_power_supplies()

        #except BaseException as e:
        #print('EXCEPTION RAISED:', e)
        #self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
        #self.logging.error(e)

        self.savePlots(plots)


    def finalise(self):
        self._finalise()

