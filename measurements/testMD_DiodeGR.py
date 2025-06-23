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
import yaml
from utils.correct_cv import lcr_series_equ, lcr_parallel_equ, lcr_error_cp

# Module structure import
from measurements import measurement

# Specific device imports for this configuration
from devices.ke2410 import * # power supply
from devices.ke6487 import * # picoammeter and votlage source for IV bias of -10 V
from devices.ke7001 import * # switch
from devices.hp4980 import * # switch

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(13,13))
    ax0 = fig.add_subplot(121)
    ax1 = fig.add_subplot(122)


    return fig, ax0, ax1

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
        #plt.cla()

        line, = ax.plot(x_vec, y_vec, color[0]+'-o', alpha=0.8)

        ax.set_title(identifier)
        #update plot label/title
        ax.set_ylabel(yaxis_title)
        ax.set_xlabel('voltage')
        plt.show()
        figManager = plt.get_current_fig_manager()
        #figManager.window.showMaximized()
        # figManager.window.state('zoomed')

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


class testMD_DiodeGR(measurement):

    def __init__(self, ide, config_path):
        super().__init__(ide)    #initialize using the base class initializer, before setting the config path. 
        self.config_path = config_path

    def initialise(self):

        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)


        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running measurements of the silicon! :)")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        ## KEITHLEY settings
        self.keithley2410_address =  8      # in the SSD lab gpib address of the power supply that does the IV scan
        self.keithley2410_ramp_address =  25  # in the SSD lab gpib address of the power supply that does the IV scan


        self.lim_cur_ke2410 = 1E-3          # compliance in [A]
        # self.lim_cur_ke6487 = 5E-7          # compliance in [A] for the GCD, this should be ?
        self.lim_vol = 10                   # compliance in [V]

        voltage_config = config['voltage_settings']
        self.Vmin_iv = voltage_config['Vmin_iv']
        self.Vmax_iv = voltage_config['Vmax_iv']
        self.Vstep_iv = voltage_config['Vstep_iv']
        
        # self.Vmin_iv = -0.5
        # self.Vmax_iv = 0.5
        # self.Vstep_iv = .1
        self.volt_list_iv = np.arange(self.Vmin_iv, self.Vmax_iv + self.Vstep_iv, self.Vstep_iv)
        #self.volt_list_iv = np.append(self.volt_list_iv,np.arange(self.Vmax_iv -self.Vstep_iv, self.Vmin_iv - self.Vstep_iv, -self.Vstep_iv))

        '''
        self.Vmin_bias_CV = -50  if '120um' in self.id else -100
        self.Vmax_bias_CV = -400 if '120um' in self.id else (-600 if '200um' in self.id else -900)
        self.Vstep_bias_CV = -50
        self.volt_list_bias_CV = np.arange(self.Vmin_bias_CV, self.Vmax_bias_CV + self.Vstep_bias_CV, self.Vstep_bias_CV)
        '''
        # self.volt_list_bias_CV = [-100, -250, -400] if '120um' in self.id else ([-200, -400, -600] if '200um' in self.id else [-400, -600, -800])
        
        '''
        self.Vmin_bias_IV = -100 if '120um' in self.id else -200
        self.Vmax_bias_IV = -400 if '120um' in self.id else (-600 if '200um' in self.id else -900)
        self.Vstep_bias_IV = -50 if '120um' in self.id else -100
        self.volt_list_bias_IV = np.arange(self.Vmin_bias_IV, self.Vmax_bias_IV + self.Vstep_bias_IV, self.Vstep_bias_IV) if not '_0kGy'in self.id else np.array([-350])
        '''
        
        # self.volt_list_bias_IV = [-100, -250, -400] if '120um' in self.id else ([-200, -400, -600] if '200um' in self.id else [-400, -600, -800])
        
        # self.volt_list_bias_IV = [-350]

        self.Vmin = voltage_config['Vmin']
        self.Vmax = voltage_config['Vmax']
        self.Vstep = voltage_config['Vstep']
        print(self.Vmin)

        # self.volt_list_bias_IV = voltage_config['volt_list_bias_IV'] if not '_0kGy' in self.id else voltage_config['volt_list_test']
        self.volt_list_bias_IV = np.arange(self.Vmax, self.Vmin + self.Vstep, self.Vstep) if not '_0kGy' in self.id else voltage_config['volt_list_test']
        # self.volt_list_bias_IV = [-350, -400]


        #self.nSampling_IV = 30 # TODO change to original 30s

        #self.delay_vol_iv = voltage_config['delay_vol_iv']      # delay between setting voltage and executing measurement in [s]

        #self.delay_initial_iv = 30  # TODO change to original 30s

        #MD to remove!
        self.nSampling_IV = 30
        self.delay_vol_iv = 10
        self.delay_ramp_iv = 1
    
        #self.delay_step_iv = 60
        #self.discharge_voltage = 10

        ## initialize the devices

        self.keithley2410 = ke2410(self.keithley2410_address)
        # self.keithley2410_ramp = ke2410(self.keithley2410_ramp_address)


        ## Set up volt meter
        self.keithley6487_address = 15
        self.keithley6487 = ke6487(self.keithley6487_address)
        self.keithley6487_address2 = 23
        self.keithley6487_2 = ke6487(self.keithley6487_address2)

    def reset_power_supplies(self):

        ## Reset power supply for CV measurement

        # self.keithley2410_ramp.ramp_down_slow()
        # self.keithley2410_ramp.set_output_off()
        # self.keithley2410_ramp.reset()
        # self.keithley2410_ramp.set_source('voltage')
        # self.keithley2410_ramp.set_sense('current')
        # self.keithley2410_ramp.set_current_limit(self.lim_cur_ke2410)
        # self.keithley2410_ramp.set_voltage(0)
        # self.keithley2410_ramp.set_terminal('rear')
        # time.sleep(3)
        # MARC keithley2410.set_interlock_on()
        # self.keithley2410_ramp.set_output_off()
        # time.sleep(1)


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
        

        self.keithley6487.ramp_down()
        self.keithley6487.reset()
        self.keithley6487.setup_ammeter()
        self.keithley6487.set_nplc(2)

        self.keithley6487_2.ramp_down()
        self.keithley6487_2.reset()
        self.keithley6487_2.setup_ammeter()
        self.keithley6487_2.set_nplc(2)
        # self.keithley6487.set_range(self.lim_cur_ke6487)

    def saveSinglePlot(self, fig, ax, name):
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(self.rdir+'/'+name, bbox_inches=extent.expanded(1.2, 1.2))
        return 0
    
    def createHeader(self):
        # IV
        ke6487_lim_vol = -999. #self.keithley6487.check_voltage_limit()
        ke6487_lim_cur = -999 ## hopefully keithley6487.check_current_limit() #self.keithley6487.check_current_limit()
        # ke2410_lim_vol  = self.keithley2410_ramp.check_voltage_limit()
        # ke2410_lim_cur  = self.keithley2410_ramp.check_current_limit()
        ke2410_lim_vol  = self.keithley2410.check_voltage_limit()
        ke2410_lim_cur  = self.keithley2410.check_current_limit()

        ke6487_lim_vol_2 = -999. #self.keithley6487.check_voltage_limit()
        ke6487_lim_cur_2 = -999 ## hopefully keithley6487.check_current_limit() #self.keithley6487.check_current_limit()

        hdIV = [
            'IV m\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke6487 second voltage limit:      %8.2E V' % ke6487_lim_vol_2,
            'Ke6487 second current limit:      %8.2E A' % ke6487_lim_cur_2,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.delay_vol_iv,
            'Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]'
        ]
        #line = [biasV, vol, cur_tot, measV, volSmall, means, errs]

        hdRV = [
            'RV Sweep\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke6487 2 voltage limit:      %8.2E V' % ke6487_lim_vol_2,
            'Ke6487 2 current limit:      %8.2E A' % ke6487_lim_cur_2,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.delay_vol_iv,
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        return(hdIV, hdRV)
   
    def IVpoint(self, biasV): # def IVpoint(self, biasV, measV):
        # self.keithley2410_ramp.ramp_voltage(measV)
        time.sleep(self.delay_ramp_iv)

        cur_tot = self.keithley2410.read_current()
        vol = self.keithley2410.read_voltage()
        # cur_totSmall = self.keithley2410_ramp.read_current()
        # volSmall = self.keithley2410_ramp.read_voltage()

        measurements = np.array([self.keithley6487.read_current() for _ in range(self.nSampling_IV)])
        measurements_2 = np.array([self.keithley6487_2.read_current() for _ in range(self.nSampling_IV)])
        #measurements = measurements[2*self.nSampling_IV:]
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.nSampling_IV)
        means_2 = np.mean(measurements_2, axis=0)
        errs_2 = np.std(measurements_2, axis=0)/math.sqrt(self.nSampling_IV)

        #TODO V bias set, V bias measured, I bias, V ramp set, V ramp meas, I ramp, I amm, err I amm
        # line = [biasV, vol, cur_tot, measV, volSmall, means, errs, means_2, errs_2, cur_totSmall]
        # line = [biasV, vol, cur_tot, biasV, biasV, means, errs, means_2, errs_2]
        line = [biasV, vol, cur_tot, means, errs, means_2, errs_2]
        self.logging.info("{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <8.3E}".format(*line))

        # if means > self.lim_cur_ke6487:
        #     self.logging.info('reached compliance in the keithley6487')
        #     raise Exception("Reached compliance in the keithley6487")
        
        return(line)

    def retrieveR(self, V, I):

        #index_3V = min(range(len(V)), key=lambda i: abs(V[i]-3))
        #G, Iq = np.polyfit(V[index_3V:], I[index_3V:], 1)
        G, Iq = np.polyfit(V, I, 1)
        return (1/G, Iq)

    def IVscan(self, name, fig, ax2, ax3, hdIV, hdRV):

        self.logging.info('\n\nSTARTING IV SCAN...\n\n')
        self.reset_power_supplies()
        # self.reset_switch()
        fname_out_IV = '_'.join(['iv', self.id, name]) + '.dat'
        fname_out_RV = '_'.join(['rv', self.id, name]) + '.dat'
        tmp_id_title = 'IV '+ name+ ': ' + self.id.replace('_m',' -').replace('_p', ' +').replace('_',' ')
        tmp_id_y_R     = r'$R$'
        tmp_id_y     = 'current'

        biasVs = []
        line2 = []
        outRV = []
        Rs_amp = []
        I_diode = []
        I_GR = []
        

        try:
            # Do IV Scan
            self.keithley2410.set_output_on()
        
            #self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t')
            # self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\t Total Current [A]\t Diode pad Current [A]')
            self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]')

            start_time = time.time()
            data_save = []

            for v in self.volt_list_bias_IV:
        
                self.keithley2410.ramp_up(v)
                time.sleep(self.delay_ramp_iv)
                # self.keithley2410_ramp.set_output_on()
                #time.sleep(self.delay_vol_iv)

                line3 = []
                Vs_amp = []
                Is_amp = []
                Is_amp2 = []
                outIV_oneBias = []
                

                # for measV in self.volt_list_iv:
                # lineIV = self.IVpoint(v, measV)
                lineIV = self.IVpoint(v)
                outIV_oneBias.append(lineIV)
                data_save.append(lineIV)
                # Recall that lineIV = [biasV, vol, cur_tot, measV, volSmall, means, errs]
                Vs_amp.append(lineIV[1])
                Is_amp.append(lineIV[3])
                Is_amp2.append(lineIV[5])
                # line3 = live_plotter(Vs_amp, Is_amp, ax3, line3, identifier="IV Curve", yaxis_title=tmp_id_y, color='g')
            
                # self.keithley2410_ramp.ramp_down_slow()
                time.sleep(self.delay_ramp_iv)
                # self.keithley2410_ramp.set_output_off()

                biasVs.append(v)
                fname_out_IV = '_'.join(['iv', self.id, name, str(v), 'V']) + '.dat'    
                # self.save_list(outIV_oneBias, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
                # self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_{c}.png".format(a=self.id, b=name, c=v))

                # [R_amp, Iq_amp] = self.retrieveR(Vs_amp, Is_amp)
                # outRV.append([v, R_amp])
                # Rs_amp.append(R_amp)
                #print(Rs_amp)
                I_GR.append(Is_amp2)
                I_diode.append(Is_amp)
            
                # line2 = live_plotter(biasVs, Rs_amp, ax2, line2, identifier="RV Curve (Amp)", yaxis_title=tmp_id_y_R, color='r')
                line2 = live_plotter(biasVs, I_GR, ax2, line2, identifier="IV Curve GR", yaxis_title=tmp_id_y, color='g')
                line3 = live_plotter(biasVs, I_diode, ax3, line3, identifier="IV Curve diode pad", yaxis_title=tmp_id_y, color='g')
                # self.save_list(outRV, fname_out_RV, fmt="%.5E", header="\n".join(hdRV))

            # self.save_list(data_save, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
            # self.saveSinglePlot(fig, ax2,"iv_{a}_{b}_GR.png".format(a=self.id, b=name))
            # self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_pad.png".format(a=self.id, b=name))

            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            self.logging.info("Elapsed time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), int(seconds)))

        
        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED IN IV SCAN:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        self.reset_power_supplies()

        self.save_list(data_save, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
        self.saveSinglePlot(fig, ax2,"iv_{a}_{b}_GR.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_pad.png".format(a=self.id, b=name))

        
        ## Save
        # self.saveSinglePlot(fig, ax2,"rv_{a}_{b}_{c}.png".format(a=self.id, b=name,c=v))
        # self.save_list(outRV, fname_out_RV, fmt="%.5E", header="\n".join(hdRV))

        self.logging.info('\n\n IV SCAN FINISHED\n\n')

    def execute(self):

        # Name of files
        name = "Test_name"

        # Create plots
        # fig, ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7 = init_liveplot()
        fig, ax3, ax2 = init_liveplot()

        ## Print header
        # [hdCV, hdIV, hdRV] = self.createHeader()
        [hdIV, hdRV] = self.createHeader()
        # for line in hdCV:
        #     self.logging.info(line)

        # self.CVscan(name, fig, ax0, ax1, ax4, ax5, ax6, ax7, hdCV)
        self.IVscan(name, fig, ax2, ax3, hdIV, hdRV)
        
    def finalise(self):
        self._finalise()