import matplotlib.pyplot as plt
plt.style.use('ggplot')
import time, math
import numpy as np
import yaml

# Module structure import
from measurements import measurement
import devices

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

class testMD_DiodeStrip(measurement):

    def __init__(self, ide, config_path):
        super().__init__(ide)
        self.config_path = config_path

    def initialise(self):

        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)


        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running test: %s" % self.__class__.__name__)
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        ## KEITHLEY settings
        # self.sourcemeter_1_address =  8      # in the SSD lab gpib address of the power supply that does the IV scan
        # self.sourcemeter_2_address =  25  # in the SSD lab gpib address of the power supply that does the IV scan


        # self.lim_cur_ke2410 = 1E-3          # compliance in [A]
        # # self.lim_cur_ke6487 = 5E-7          # compliance in [A] for the GCD, this should be ?
        # self.lim_vol = 10                   # compliance in [V]


        self.volt_list_iv = np.arange(self.config['devices']['sourcemeter_1']['range_iv']['Vmin_iv'], 
                                      self.config['devices']['sourcemeter_1']['range_iv']['Vmax_iv'] + 
                                      self.config['devices']['sourcemeter_1']['range_iv']['Vstep_iv'], 
                                      self.config['devices']['sourcemeter_1']['range_iv']['Vstep_iv'])
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

        # self.volt_list_bias_IV = voltage_config['volt_list_bias_IV'] if not '_0kGy' in self.id else voltage_config['volt_list_test']
        # self.volt_list_bias_IV = np.arange(self.Vmin, self.Vmax + self.Vstep, self.Vstep)
        # self.volt_list_bias_IV = [-350, -400]
        self.volt_list_bias_IV = np.arange(self.config['devices']['sourcemeter_1']['range']['Vmax'], 
                                           self.config['devices']['sourcemeter_1']['range']['Vmin'] + 
                                           self.config['devices']['sourcemeter_1']['range']['Vstep'], 
                                           self.config['devices']['sourcemeter_1']['range']['Vstep']) 
        # if not '_0kGy' in self.id else self.config['devices']['sourcemeter']['volt_list_test']


        #self.config['devices']['sourcemeter_1']['n_sampling'] = 30 # TODO change to original 30s

        #self.config['devices']['sourcemeter_1']['delay_vol'] = voltage_config['delay_vol_iv']      # delay between setting voltage and executing measurement in [s]

        #self.delay_initial_iv = 30  # TODO change to original 30s

        #MD to remove!
        # self.config['devices']['sourcemeter_1']['n_sampling'] = 100 #used
        # self.config['devices']['sourcemeter_1']['delay_vol'] = 10 #used 
        # self.config['devices']['sourcemeter_1']['delay_ramp'] = 1 #used
    
        #self.delay_step_iv = 60
        #self.discharge_voltage = 10

        ## initialize the devices


        ## Set up sourcemeter
        sourcemeter_1_class = getattr(devices, self.config['devices']['sourcemeter_1']['model'])
        self.sourcemeter_1 = sourcemeter_1_class(self.config['devices']['sourcemeter_1']['address'])
        sourcemeter_2_class = getattr(devices, self.config['devices']['sourcemeter_2']['model'])     #in case of different sourcemeter types
        self.sourcemeter_2 = sourcemeter_2_class(self.config['devices']['sourcemeter_2']['address'])


        # self.sourcemeter_1 = ke2410(self.sourcemeter_1_address)
        # self.sourcemeter_2 = ke2410(self.sourcemeter_2_address)

        # set up picoammeter
        picoammeter_class = getattr(devices, self.config['devices']['picoammeter']['model'])
        self.picoammeter = picoammeter_class(self.config['devices']['picoammeter']['address'])

        # ## Set up volt meter
        # self.picoammeter_address = 15
        # self.picoammeter = ke6487(self.picoammeter_address)

    def reset_power_supplies(self):

        ## Reset power supply for CV measurement

        self.sourcemeter_2.ramp_down_slow()
        self.sourcemeter_2.set_output_off()
        self.sourcemeter_2.reset()
        self.sourcemeter_2.set_source('voltage')
        self.sourcemeter_2.set_sense('current')
        self.sourcemeter_2.set_current_limit(self.config['devices']['sourcemeter_2']['lim_cur'])
        self.sourcemeter_2.set_voltage(0)
        self.sourcemeter_2.set_terminal('rear')
        time.sleep(3)
        # MARC keithley2410.set_interlock_on()
        self.sourcemeter_2.set_output_off()
        time.sleep(1)


        self.sourcemeter_1.ramp_down()
        self.sourcemeter_1.set_output_off()
        self.sourcemeter_1.reset()
        self.sourcemeter_1.set_source('voltage')
        self.sourcemeter_1.set_sense('current')
        self.sourcemeter_1.set_current_limit(self.config['devices']['sourcemeter_1']['lim_cur'])
        self.sourcemeter_1.set_voltage(0)
        self.sourcemeter_1.set_terminal('rear')
        time.sleep(3)
        # MARC keithley2410.set_interlock_on()
        self.sourcemeter_1.set_output_off()
        time.sleep(1)
        

        self.picoammeter.ramp_down()
        self.picoammeter.reset()
        self.picoammeter.setup_ammeter()
        self.picoammeter.set_nplc(2)
        # self.picoammeter.set_range(self.lim_cur_ke6487)

    def saveSinglePlot(self, fig, ax, name):
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(self.rdir+'/'+name, bbox_inches=extent.expanded(1.2, 1.2))
        return 0
    
    #TODO: Read dynamically from config
    def createHeader(self):
        # IV
        picoammeter_lim_vol = -999. #self.picoammeter.check_voltage_limit()
        picoammeter_lim_cur = -999 ## hopefully keithley6487.check_current_limit() #self.picoammeter.check_current_limit()
        sourcemeter_lim_vol  = self.sourcemeter_2.check_voltage_limit()
        sourcemeter_lim_cur  = self.sourcemeter_2.check_current_limit()

        hdIV = [
            'IV m\n',
            'Measurement Settings:',
            'picoammeter voltage limit:      %8.2E V' % picoammeter_lim_vol,
            'picoammeter current limit:      %8.2E A' % picoammeter_lim_cur,
            'sourcemeter voltage limit:      %8.2E V' % sourcemeter_lim_vol,
            'sourcemeter current limit:      %8.2E A' % sourcemeter_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['devices']['sourcemeter_1']['delay_vol'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]'
        ]
        #line = [biasV, vol, cur_tot, measV, volSmall, means, errs]

        hdRV = [
            'RV Sweep\n',
            'Measurement Settings:',
            'picoammeter voltage limit:      %8.2E V' % picoammeter_lim_vol,
            'picoammeter current limit:      %8.2E A' % picoammeter_lim_cur,
            'sourcemeter voltage limit:      %8.2E V' % sourcemeter_lim_vol,
            'sourcemeter current limit:      %8.2E A' % sourcemeter_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['devices']['sourcemeter_1']['delay_vol'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        return(hdIV, hdRV)

    def IVpoint(self, biasV, measV):
        self.sourcemeter_2.ramp_voltage(measV)
        time.sleep(self.config['devices']['sourcemeter_1']['delay_ramp'])

        cur_tot = self.sourcemeter_1.read_current()
        vol = self.sourcemeter_1.read_voltage()
        cur_totSmall = self.sourcemeter_2.read_current()
        volSmall = self.sourcemeter_2.read_voltage()

        measurements = np.array([self.picoammeter.read_current() for _ in range(self.config['devices']['sourcemeter_1']['n_sampling'])])
        #measurements = measurements[2*self.config['devices']['sourcemeter_1']['n_sampling']:]
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.config['devices']['sourcemeter_1']['n_sampling'])

        #TODO V bias set, V bias measured, I bias, V ramp set, V ramp meas, I ramp, I amm, err I amm
        line = [biasV, vol, cur_tot, measV, volSmall, means, errs, cur_totSmall]
        self.logging.info("{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <8.3E}\t{: <8.3E}".format(*line))

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
        

        try:
            # Do IV Scan
            self.sourcemeter_1.set_output_on()
        
            #self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t')
            self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]')

            start_time = time.time()

            for v in self.volt_list_bias_IV:
        
                self.sourcemeter_1.ramp_up(v)
                time.sleep(self.config['devices']['sourcemeter_1']['delay_ramp'])
                self.sourcemeter_2.set_output_on()
                time.sleep(self.config['devices']['sourcemeter_1']['delay_vol'])

                line3 = []
                Vs_amp = []
                Is_amp = []
                outIV_oneBias = []
                

                for measV in self.volt_list_iv:
                    lineIV = self.IVpoint(v, measV)
                    outIV_oneBias.append(lineIV)
                    # Recall that lineIV = [biasV, vol, cur_tot, measV, volSmall, means, errs]
                    Vs_amp.append(lineIV[4])
                    Is_amp.append(lineIV[5])
                    line3 = live_plotter(Vs_amp, Is_amp, ax3, line3, identifier="IV Curve", yaxis_title=tmp_id_y, color='g')
            
                self.sourcemeter_2.ramp_down_slow()
                time.sleep(self.config['devices']['sourcemeter_1']['delay_ramp'])
                self.sourcemeter_2.set_output_off()

                biasVs.append(v)
                fname_out_IV = '_'.join(['iv', self.id, name, str(v), 'V']) + '.dat'    
                self.save_list(outIV_oneBias, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
                self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_{c}.png".format(a=self.id, b=name, c=v))

                [R_amp, Iq_amp] = self.retrieveR(Vs_amp, Is_amp)
                outRV.append([v, R_amp])
                Rs_amp.append(R_amp)
                #print(Rs_amp)
            
                line2 = live_plotter(biasVs, Rs_amp, ax2, line2, identifier="RV Curve (Amp)", yaxis_title=tmp_id_y_R, color='r')
                self.save_list(outRV, fname_out_RV, fmt="%.5E", header="\n".join(hdRV))

            self.saveSinglePlot(fig, ax2,"rv_{a}_{b}.png".format(a=self.id, b=name))

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
        
        ## Save
        # self.saveSinglePlot(fig, ax2,"rv_{a}_{b}_{c}.png".format(a=self.id, b=name,c=v))
        # self.save_list(outRV, fname_out_RV, fmt="%.5E", header="\n".join(hdRV))

        self.logging.info('\n\n IV SCAN FINISHED\n\n')

    def execute(self):

        # Name of files
        name =  self.__class__.__name__

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