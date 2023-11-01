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
    ax0 = fig.add_subplot(221)
    ax1 = fig.add_subplot(222)
    ax2 = fig.add_subplot(223)
    ax3 = fig.add_subplot(224)

    return fig, ax0, ax1, ax2, ax3

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
        ax.clear()
        plt.cla()

        line, = ax.plot(x_vec, y_vec, color[0]+'-o', alpha=0.8)

        ax.set_title(identifier)
        #update plot label/title
        ax.set_ylabel(yaxis_title)
        ax.set_xlabel('voltage')
        plt.show()
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()

    line.set_xdata(x_vec)
    line.set_ydata(y_vec)

    '''
    # adjust limits if new data goes beyond bounds
    if np.min(y_vec)<=line.axes.get_ylim()[0] or np.max(y_vec)>=line.axes.get_ylim()[1]:
        ax.set_ylim([np.min(y_vec)-np.std(y_vec),np.max(y_vec)+np.std(y_vec)])
    if np.min(x_vec)<=line.axes.get_xlim()[0] or np.max(x_vec)>=line.axes.get_xlim()[1]:
        ax.set_xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])
    '''
    
    
    ax.set_ylim([np.min(y_vec)-0.005*abs(np.min(y_vec)),np.max(y_vec)+0.005*abs(np.max(y_vec))])
    #ax.set_xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])
    ax.set_xlim([np.min(x_vec)-0.5,np.max(x_vec)+0.5])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    #mypause(pause_time)

    return line


class testMD_fullStrip(measurement):
    """Measurement of a dummy I-V curve. """

    def initialise(self):

        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running all 3 measurements of the silicon! :)")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        ## KEITHLEY settings
        self.keithley2410_address =  8      # in the SSD lab gpib address of the power supply that does the IV scan
        self.keithley2410_ramp_address =  25  # in the SSD lab gpib address of the power supply that does the IV scan

        self.keithley2410_gcddiode_address = 8
        self.switch_address       = 7       # gpib address of the switch

        ## LCR meter settings
        self.lcr_meter_address = 17         # in the SSD lab this is 9
        self.lcr_vol = 0.250 #0.501         # ac voltage amplitude in [mV]
        self.lcr_freq = 10000               # ac voltage frequency in [Hz]
        self.cv_res = 1e6                   # cv parallel resistor in [Ohm]
        
        self.lcr_vol = 1 #0.501             # ac voltage amplitude in [mV]
        self.lcr_freq = 1E6                 # ac voltage frequency in [Hz]       


        self.lim_cur_ke2410 = 1E-5          # compliance in [A]
        self.lim_cur_ke6487 = 5E-7          # compliance in [A] for the GCD, this should be ?
        self.lim_vol = 10                   # compliance in [V]

        '''
        self.Vmin_cv = -50
        self.Vmax_cv = -500
        self.Vstep_cv = -50
        self.volt_list_cv = np.arange(self.Vmin_cv, self.Vmax_cv + self.Vstep_cv, self.Vstep_cv)
        '''
        
        self.Vmin_iv = 0
        self.Vmax_iv = 10
        self.Vstep_iv = 1
        self.volt_list_iv = np.arange(self.Vmin_iv, self.Vmax_iv + self.Vstep_iv, self.Vstep_iv)
        
        self.Vmin_bias_CV = -100
        self.Vmax_bias_CV = -1000
        self.Vstep_bias_CV = -25
        self.volt_list_bias_CV = np.arange(self.Vmin_bias_CV, self.Vmax_bias_CV + self.Vstep_bias_CV, self.Vstep_bias_CV)

        self.Vmin_bias_IV = -100
        self.Vmax_bias_IV = -1000
        self.Vstep_bias_IV = -50
        self.volt_list_bias_IV = np.arange(self.Vmin_bias_IV, self.Vmax_bias_IV + self.Vstep_bias_IV, self.Vstep_bias_IV)

        self.nSampling_CV =  10
        self.nSampling_IV = 30 # TODO change to original 30s

        self.delay_vol_cv = 10     # delay between setting voltage and executing measurement in [s]
        self.delay_vol_iv = 10     # delay between setting voltage and executing measurement in [s]

        self.delay_initial_iv = 30  # TODO change to original 30s

        ## initialize the devices

        self.keithley2410 = ke2410(self.keithley2410_address)
        self.keithley2410_ramp = ke2410(self.keithley2410_ramp_address)


        self.switch       = ke7001(self.switch_address)
        self.reset_switch()

        ## Set up lcr meter
        self.lcr_meter = hp4980(self.lcr_meter_address)
        self.lcr_meter.reset()
        self.lcr_meter.set_voltage(self.lcr_vol)
        self.lcr_meter.set_frequency(self.lcr_freq)
        self.lcr_meter.set_mode('RX')

        ## Set up volt meter
        self.keithley6487_address = 15
        self.keithley6487 = ke6487(self.keithley6487_address)


    def reset_power_supplies(self):

        ## Reset power supply for CV measurement

        self.keithley2410_ramp.ramp_down_slow()
        self.keithley2410_ramp.set_output_off()
        self.keithley2410_ramp.reset()
        self.keithley2410_ramp.set_source('voltage')
        self.keithley2410_ramp.set_sense('current')
        self.keithley2410_ramp.set_current_limit(self.lim_cur_ke2410)
        self.keithley2410_ramp.set_voltage(0)
        self.keithley2410_ramp.set_terminal('rear')
        time.sleep(3)
        # MARC keithley2410.set_interlock_on()
        self.keithley2410_ramp.set_output_off()
        time.sleep(1)


        self.keithley2410.ramp_down()
        self.keithley2410.set_output_off()
        self.keithley2410.reset()
        self.keithley2410.set_source('voltage')
        self.keithley2410.set_sense('current')
        self.keithley2410.set_current_limit(self.lim_cur_ke2410)
        self.keithley2410.set_voltage(0)
        self.keithley2410.set_terminal('rear')
        time.sleep(3)
        # MARC keithley2410.set_interlock_on()
        self.keithley2410.set_output_off()
        time.sleep(1)
        

        ## Reset power supply of the second keithley which biases the gcd diode
        #self.keithley2410_gcddiode.ramp_voltage(0)
        #self.keithley2410_gcddiode.set_output_off()
        #self.keithley2410_gcddiode.reset()
        #self.keithley2410_gcddiode.set_source('voltage')
        #self.keithley2410_gcddiode.set_sense('current')
        #self.keithley2410_gcddiode.set_current_limit(self.lim_cur_ke2410)
        #self.keithley2410_gcddiode.set_voltage(0)
        #self.keithley2410_gcddiode.set_terminal('rear')
        # MARC keithley2410_gcddiode.set_interlock_on()
        #self.keithley2410_gcddiode.set_output_off()
        #time.sleep(1)

        self.keithley6487.ramp_down()
        self.keithley6487.reset()
        self.keithley6487.setup_ammeter()
        self.keithley6487.set_nplc(2)
        self.keithley6487.set_range(self.lim_cur_ke6487)

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
            if 'cv' in name:
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 7], np.array(val)[:, 7] * 0.01, \
                                 'Bias Voltage [V]', 'Parallel Capacitance [F]',  'CV ' + self.id + ' ' +name, fn="cv_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[2:, 1], np.array(val)[2:, 7]**(-2), 0, \
                                 'Bias Voltage [V]', '1/C^2 [1/F^2]',  '1/C2 ' + self.id + ' ' + name, fn="1c2v_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 9], np.array(val)[:, 9]*0.01, \
                                 'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_total_current_{a}_{b}.png".format(a=self.id, b=name))

            elif 'iv' in name:
                self.newPlotIV(np.array(val)[:, 1], np.array(val)[:, 2])
                #self.newMarkdownIV()

                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 2], np.array(val)[:, 3], \
                                 'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array([val for val in val if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 1], \
                                 np.array([val for val in val if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 2], \
                                 np.array([val for val in val if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 3], \
                                 'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_zoom_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 4], np.array(val)[:, 4]*0.01, \
                                 'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_total_current_{a}_{b}.png".format(a=self.id, b=name))


    def newMarkdownIV(self):
        reportFile = open("logs/"+self.id+"/IV_report.md", "w", encoding="utf-8")

        data = self.id.split('_')

        text = "## Sensor " + self.id + "\n" 
        text += "#### General characteristics\n"

        text += "\n"

        text += "|      Field     |     Value    |\n"
        text += "|:--------------:|:------------:|\n"
        text += "|   Oxide type   |       "+data[0]+"      |\n"
        text += "| Thickness (μm) |      300     |\n"
        text += "|   Sensor type  | Tracker-like |\n"
        text += "|   Irradiated   |      No      |\n"

        text += "\n"

        text += "|       Field      |   Value  |\n"
        text += "|:----------------:|:--------:|\n"
        text += "|   Batch number   |     ?    |\n"
        text += "|   Sensor number  |     "+data[1]+"    |\n"
        text += "| Connected strips | 29,30,31 |\n"
        
        text += "\n"
        
        text += "#### "+data[2]+" measurement\n"

        reportFile.write(text)
        reportFile.close()






    def newPlotIV(self, v, i):

        supertitle = self.id 
        mixlabel = "Interstrip voltage (V)"
        miylabelC = "Measured current (A)"


        fig, ax10 = subplots(1, 1, figsize=(15, 10))  #subplots(1, 2, figsize=(15, 10))

        fig.suptitle("Measurement for interstrip properties", fontsize=24)
        fig.tight_layout()

        ax10.plot(v,i)
        ax10.plot(v,i,'x')
        ax10.set_ylabel(miylabelC, fontsize=14)
        ax10.set_xlabel(mixlabel, fontsize=14)
        ax10.grid()
        for item in ([ax10.title, ax10.xaxis.label, ax10.yaxis.label] + ax10.get_xticklabels() + ax10.get_yticklabels()):
            item.set_fontsize(12)
        ax10.xaxis.set_major_locator(MaxNLocator(6))
        ax10.yaxis.set_major_locator(MaxNLocator(6))
        ax10.xaxis.set_minor_locator(AutoMinorLocator())
        ax10.yaxis.set_minor_locator(AutoMinorLocator())
        ax10.set_title(supertitle, fontsize=18)
        #ax10[0].set_title("Average: "+str(mu)+"  Std: "+str(std)+"  N:"+str(N))
        ax10.tick_params(axis='both', which='both', direction="in")
        ax10.set_xlim(v[0],v[-1])


        savefig("logs/"+supertitle+"/IV.png",bbox_inches='tight')


    def createHeader(self):
        # CV
        lim_vol  = self.keithley2410.check_voltage_limit()
        lim_cur  = self.keithley2410.check_current_limit()
        lcr_vol  = float(self.lcr_meter.check_voltage())
        lcr_freq = float(self.lcr_meter.check_frequency())

        # IV
        ke6487_lim_vol = -999. #self.keithley6487.check_voltage_limit()
        ke6487_lim_cur = self.lim_cur_ke6487 ## hopefully keithley6487.check_current_limit() #self.keithley6487.check_current_limit()
        ke2410_lim_vol  = self.keithley2410_ramp.check_voltage_limit()
        ke2410_lim_cur  = self.keithley2410_ramp.check_current_limit()

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

        hdIV = [
            'IV Sweep\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.delay_vol_iv,
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        hdRV = [
            'RV Sweep\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.delay_vol_iv,
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        return(hdCV, hdIV, hdRV)




    def CRVpoint(self, biasV, channel):  ## don't really know how best to do this ... to be teasted on the setup

        self.switch.close_channel(channel)
        self.keithley2410.set_output_on()
        self.keithley2410.ramp_up(biasV)
        self.keithley2410_ramp.set_output_on()
        self.keithley2410_ramp.ramp_up(0)
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





    def IVpoint(self, biasV, measV):
        self.keithley2410_ramp.ramp_voltage(measV)
        if measV == 0:
            time.sleep(self.delay_initial_iv-self.delay_vol_iv)
        time.sleep(self.delay_vol_iv)

        cur_tot = self.keithley2410_ramp.read_current()
        vol = self.keithley2410_ramp.read_voltage()

        measurements = np.array([self.keithley6487.read_current() for _ in range(self.nSampling_IV)])
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.nSampling_IV)


        line = [biasV, vol, means, errs, cur_tot]
        self.logging.info("{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        if means > self.lim_cur_ke6487:
            self.logging.info('reached compliance in the keithley6487')
            raise Exception("Reached compliance in the keithley6487")
        
        return(line)


    def retrieveR(self, V, I):

        # That 3 is making linear regression from 3V to 5V
        index_3V = min(range(len(V)), key=lambda i: abs(V[i]-3))
        G, Iq = np.polyfit(V[index_3V:], I[index_3V:], 1)
        return (1/G, Iq)
        






    def CVscan(self, name, fig, ax0, ax1, hdCV):

        self.logging.info('\n\nSTARTING CV SCAN...\n\n')
        fname_out_CV = '_'.join(['cv', self.id, name]) + '.dat'
        biasVs = []
        Rs_LCR = []
        Cs_LCR = []
        line0 = []
        line1 = []
        outCV = []
        color = 'b'
        tmp_id_y_R     = r'$R$'
        tmp_id_y_C     = r'$C$'


        self.reset_power_supplies()
        self.reset_switch()


         # Do CV Scan
        try:            
            self.logging.info("Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]")    
                
            for v in self.volt_list_bias_CV:
                
                lineCV = self.CRVpoint(v, 1)
                outCV.append(lineCV)
                # Recall that lineCV = [biasV, vol, self.lcr_freq, r, dr, x, dx, c_s, c_p, cur_tot]
                biasVs.append(lineCV[0])
                Rs_LCR.append(lineCV[3])
                Cs_LCR.append(lineCV[8])                
                line0 = live_plotter(biasVs, Rs_LCR, ax0, line0, identifier="RV curve (LCR)", yaxis_title=tmp_id_y_R, color=color)
                line1 = live_plotter(biasVs, Cs_LCR, ax1, line1, identifier="CV curve", yaxis_title=tmp_id_y_C, color=color)

        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED IN CV SCAN:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        self.reset_power_supplies()
        self.reset_switch()

        self.saveSinglePlot(fig, ax1,"cv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax0,"rv_LCR_{a}_{b}.png".format(a=self.id, b=name))

        self.save_list(outCV, fname_out_CV, fmt="%.5E", header="\n".join(hdCV))

        self.logging.info('\n\n CV SCAN FINISHED\n\n')




    def IVscan(self, name, fig, ax2, ax3, hdIV, hdRV):

        self.logging.info('\n\nSTARTING IV SCAN...\n\n')
        self.reset_power_supplies()
        self.reset_switch()
        fname_out_IV = '_'.join(['iv', self.id, name]) + '.dat'
        fname_out_RV = '_'.join(['rv', self.id, name]) + '.dat'
        tmp_id_title = 'IV '+ name+ ': ' + self.id.replace('_m',' -').replace('_p', ' +').replace('_',' ')
        tmp_id_y_R     = r'$R$'
        tmp_id_y     = 'current'

        biasVs = []
        line2 = []
        outRV = []
        Rs_amp = []
        

        try:
            # Do IV Scan
            self.switch.close_channel(3)
            self.keithley2410.set_output_on()
            self.keithley2410_ramp.set_output_on()
            self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t')
            
            

            for v in self.volt_list_bias_IV:
                
                self.keithley2410.ramp_up(v)
                self.keithley2410_ramp.ramp_voltage(0)
                time.sleep(self.delay_initial_iv)

                line3 = []
                Vs_amp = []
                Is_amp = []
                outIV_oneBias = []
                

                for measV in self.volt_list_iv:
                    lineIV = self.IVpoint(v, measV)
                    outIV_oneBias.append(lineIV)
                    # Recall that lineIV = [biasV, vol, means, errs, cur_tot]
                    Vs_amp.append(lineIV[1])
                    Is_amp.append(lineIV[2])
                    line3 = live_plotter(Vs_amp, Is_amp, ax3, line3, identifier="IV Curve", yaxis_title=tmp_id_y, color='g')
            
                self.keithley2410_ramp.ramp_down_slow()
                time.sleep(self.delay_vol_iv)
                biasVs.append(v)
                fname_out_IV = '_'.join(['iv', self.id, name, str(v), 'V']) + '.dat'    
                self.save_list(outIV_oneBias, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
                self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_{c}.png".format(a=self.id, b=name, c=v))

                [R_amp, Iq_amp] = self.retrieveR(Vs_amp, Is_amp)
                outRV.append([v, R_amp])
                Rs_amp.append(R_amp)
            
                line2 = live_plotter(biasVs, Rs_amp, ax2, line2, identifier="RV Curve (Amp)", yaxis_title=tmp_id_y_R, color='r')
        
        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED IN IV SCAN:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        self.reset_power_supplies()
        self.reset_switch()
        
        ## Save
        self.saveSinglePlot(fig, ax2,"rv_{a}_{b}.png".format(a=self.id, b=name))
        self.save_list(outRV, fname_out_RV, fmt="%.5E", header="\n".join(hdRV))

        self.logging.info('\n\n IV SCAN FINISHED\n\n')









    def execute(self):

        # Name of files
        name = "Test_name"

        # Create plots
        fig, ax0, ax1, ax2, ax3 = init_liveplot()

        ## Print header
        [hdCV, hdIV, hdRV] = self.createHeader()
        for line in hdCV:
            self.logging.info(line)

        self.CVscan(name, fig, ax0, ax1, hdCV)
        self.IVscan(name, fig, ax2, ax3, hdIV, hdRV)
        

    def finalise(self):
        self._finalise()