import matplotlib.pyplot as plt
plt.style.use('ggplot')
import time, math
import numpy as np
import yaml

#TODO: move general imports to base measurement class

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
            self.config = yaml.safe_load(file)


        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running test: %s" % self.__class__.__name__)
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        self.volt_list_iv = np.arange(self.config['devices']['sourcemeter']['range_iv']['Vmin_iv'], 
                                      self.config['devices']['sourcemeter']['range_iv']['Vmax_iv'] + 
                                      self.config['devices']['sourcemeter']['range_iv']['Vstep_iv'], 
                                      self.config['devices']['sourcemeter']['range_iv']['Vstep_iv'])
 
        self.volt_list_bias_IV = np.arange(self.config['devices']['sourcemeter']['range']['Vmax'], 
                                           self.config['devices']['sourcemeter']['range']['Vmin'] + 
                                           self.config['devices']['sourcemeter']['range']['Vstep'], 
                                           self.config['devices']['sourcemeter']['range']['Vstep']) if not '_0kGy' in self.id else self.config['devices']['sourcemeter']['volt_list_test']

        ## Set up sourcemeter
        sourcemeter_class = getattr(devices, self.config['devices']['sourcemeter']['model'])
        self.sourcemeter = sourcemeter_class(self.config['devices']['sourcemeter']['address'])
        ## Lots of references to self.sourcemeter_ramp, this should be setup similarly here if it ever needs to be included. 

        ## Set up volt meter
        picoammeter_1_class = getattr(devices, self.config['devices']['picoammeter_1']['model'])
        self.picoammeter_1 = picoammeter_1_class(self.config['devices']['picoammeter_1']['address'])
        picoammeter_2_class = getattr(devices, self.config['devices']['picoammeter_2']['model'])        #this is repeated in case the picoammeter_2 is not the same model as picoammeter_1
        self.picoammeter_2 = picoammeter_2_class(self.config['devices']['picoammeter_2']['address'])

    #TODO: refactor since it also resets the picoammeter
    def reset_power_supplies(self):

        self.sourcemeter.ramp_down()
        self.sourcemeter.set_output_off()
        self.sourcemeter.reset()
        self.sourcemeter.set_source('voltage')
        self.sourcemeter.set_sense('current')
        self.sourcemeter.set_current_limit(self.config['devices']['sourcemeter']['lim_cur'])
        self.sourcemeter.set_voltage(0)
        self.sourcemeter.set_terminal('rear')
        time.sleep(3)
        self.sourcemeter.set_output_off()
        time.sleep(1)
        

        self.picoammeter_1.ramp_down()
        self.picoammeter_1.reset()
        self.picoammeter_1.setup_ammeter()
        self.picoammeter_1.set_nplc(2)

        self.picoammeter_2.ramp_down()
        self.picoammeter_2.reset()
        self.picoammeter_2.setup_ammeter()
        self.picoammeter_2.set_nplc(2)

    def saveSinglePlot(self, fig, ax, name):
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(self.rdir+'/'+name, bbox_inches=extent.expanded(1.2, 1.2))
        return 0
    
    #TODO: dynamically read this from the config file
    def createHeader(self):
        # IV
        picoammeter_lim_vol = -999. #self.picoammeter_1.check_voltage_limit()
        picoammeter_lim_cur = -999 ## hopefully keithley6487.check_current_limit() #self.picoammeter_1.check_current_limit()
        # sourcemeter_lim_vol  = self.sourcemeter_ramp.check_voltage_limit()
        # sourcemeter_lim_cur  = self.sourcemeter_ramp.check_current_limit()
        sourcemeter_lim_vol  =   self.sourcemeter.check_voltage_limit()
        sourcemeter_lim_cur  =   self.sourcemeter.check_current_limit()

        picoammeter_lim_vol_2 = -999. #self.picoammeter_1.check_voltage_limit()
        picoammeter_lim_cur_2 = -999 ## hopefully keithley6487.check_current_limit() #self.picoammeter_1.check_current_limit()

        hdIV = [
            'IV m\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % picoammeter_lim_vol,
            'Ke6487 current limit:      %8.2E A' % picoammeter_lim_cur,
            'Ke6487 second voltage limit:      %8.2E V' % picoammeter_lim_vol_2,
            'Ke6487 second current limit:      %8.2E A' % picoammeter_lim_cur_2,
            'Ke2410 voltage limit:      %8.2E V' % sourcemeter_lim_vol,
            'Ke2410 current limit:      %8.2E A' % sourcemeter_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['devices']['sourcemeter']['delay_vol'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]'
        ]
        #line = [biasV, vol, cur_tot, measV, volSmall, means, errs]

        hdRV = [
            'RV Sweep\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % picoammeter_lim_vol,
            'Ke6487 current limit:      %8.2E A' % picoammeter_lim_cur,
            'Ke6487 2 voltage limit:      %8.2E V' % picoammeter_lim_vol_2,
            'Ke6487 2 current limit:      %8.2E A' % picoammeter_lim_cur_2,
            'Ke2410 voltage limit:      %8.2E V' % sourcemeter_lim_vol,
            'Ke2410 current limit:      %8.2E A' % sourcemeter_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['devices']['sourcemeter']['delay_vol'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        return(hdIV, hdRV)
   
    def IVpoint(self, biasV): # def IVpoint(self, biasV, measV):
        #   self.sourcemeter_ramp.ramp_voltage(measV)
        time.sleep(self.config['devices']['sourcemeter']['delay_vol'])

        cur_tot =   self.sourcemeter.read_current()
        vol =   self.sourcemeter.read_voltage()
        # cur_totSmall =    self.sourcemeter_ramp.read_current()
        # volSmall =    self.sourcemeter_ramp.read_voltage()

        measurements = np.array([self.picoammeter_1.read_current() for _ in range(self.config['devices']['picoammeter_1']['n_sampling'])])
        measurements_2 = np.array([self.picoammeter_2.read_current() for _ in range(self.config['devices']['picoammeter_1']['n_sampling'])])
        #measurements = measurements[2*self.config['devices']['picoammeter_1']['n_sampling']:]
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.config['devices']['picoammeter_1']['n_sampling'])
        means_2 = np.mean(measurements_2, axis=0)
        errs_2 = np.std(measurements_2, axis=0)/math.sqrt(self.config['devices']['picoammeter_1']['n_sampling'])

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
            self.sourcemeter.set_output_on()
            self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]')

            start_time = time.time()
            data_save = []

            for v in self.volt_list_bias_IV:
        
                self.sourcemeter.ramp_up(v)
                time.sleep(self.config['devices']['sourcemeter']['delay_vol'])
                #   self.sourcemeter_ramp.set_output_on()
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
            
                #   self.sourcemeter_ramp.ramp_down_slow()
                time.sleep(self.config['devices']['sourcemeter']['delay_vol'])
                #   self.sourcemeter_ramp.set_output_off()

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