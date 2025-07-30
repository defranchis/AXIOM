import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')  # TODO:    THIS SHOULD REALLY BE MOVED TO THE BASE MEASUREMENT CLASS SO THAT EVERY MEASUREMENT USES QT5Agg
plt.style.use('ggplot')
import time, math
import numpy as np

#TODO: move general imports to base measurement class

# Module structure import
from measurements import measurement

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(13,13))
    ax0 = fig.add_subplot(121)
    ax1 = fig.add_subplot(122)
    figManager = plt.get_current_fig_manager()
    # Maximize window depending on backend
    # The is caused by of the lack of a virtual environment, if we used that we could completely avoid these random inconsistencies.
    figManager.window.showMaximized()  # This works for Qt5Agg backend
    # Add more backends as needed

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

    line.set_xdata(x_vec)
    line.set_ydata(y_vec) 
    
    ax.set_ylim([np.min(y_vec)-0.005*abs(np.min(y_vec)),np.max(y_vec)+0.005*abs(np.max(y_vec))])
    ax.set_xlim([np.min(x_vec)-0.5,np.max(x_vec)+0.5])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    #mypause(pause_time)

    return line

class diodeIV(measurement):

    def __init__(self, config=None, current_dose=None, n_annealing = None, **kwargs):
        super().__init__(config=config, current_dose=current_dose, n_annealing=n_annealing)
        

    def initialise(self):

        # self.logging.info("\t")
        # self.logging.info("------------------------------------------")
        # self.logging.info("Running test: %s" % self.__class__.__name__)
        # self.logging.info("------------------------------------------")
        # self.logging.info(self.__doc__)
        # self.logging.info("\t")

        self._initialise()
        self._initialise_devices()
        
        # IV measurement voltage sweep range
        self.volt_list_iv = np.arange(
            self.config['measurements']['IV']['measurement_range']['v_start'],
            self.config['measurements']['IV']['measurement_range']['v_end'] + self.config['measurements']['IV']['measurement_range']['step_size'],
            self.config['measurements']['IV']['measurement_range']['step_size']
        )

        # IV bias voltage sweep range
        self.volt_list_bias_IV = np.arange(
            self.config['measurements']['IV']['bias_range']['v_start'],
            self.config['measurements']['IV']['bias_range']['v_end'] + self.config['measurements']['IV']['bias_range']['step_size'],
            self.config['measurements']['IV']['bias_range']['step_size']
        )

        # ## Set up sourcemeter
        # self.sourcemeter_1 = getattr(devices, self.config['devices']['sourcemeter_1']['model'])(self.config['devices']['sourcemeter_1']['address'])

        # ## Set up volt meters
        # self.picoammeter_1 = getattr(devices, self.config['devices']['picoammeter_1']['model'])(self.config['devices']['picoammeter_1']['address'])
        # self.picoammeter_2 = getattr(devices, self.config['devices']['picoammeter_2']['model'])(self.config['devices']['picoammeter_2']['address'])

    #TODO: refactor since it also resets the picoammeters
    def reset_power_supplies(self):

        self.sourcemeter_1.ramp_down()
        self.sourcemeter_1.set_output_off()
        self.sourcemeter_1.reset()
        self.sourcemeter_1.set_source('voltage')
        self.sourcemeter_1.set_sense('current')
        self.sourcemeter_1.set_current_limit(self.config['devices']['sourcemeter_1']['lim_cur'])
        self.sourcemeter_1.set_voltage(0)
        self.sourcemeter_1.set_terminal('rear')
        time.sleep(3)
        self.sourcemeter_1.set_output_off()
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
        sourcemeter_lim_vol  =   self.sourcemeter_1.check_voltage_limit()
        sourcemeter_lim_cur  =   self.sourcemeter_1.check_current_limit()

        picoammeter_lim_vol_2 = -999. #self.picoammeter_1.check_voltage_limit()
        picoammeter_lim_cur_2 = -999 ## hopefully keithley6487.check_current_limit() #self.picoammeter_1.check_current_limit()

        hdIV = [
            'IV m\n',
            'Measurement Settings:',
            'Picoammeter voltage limit:      %8.2E V' % picoammeter_lim_vol,
            'Picoammeter current limit:      %8.2E A' % picoammeter_lim_cur,
            'Picoammeter second voltage limit:      %8.2E V' % picoammeter_lim_vol_2,
            'Picoammeter second current limit:      %8.2E A' % picoammeter_lim_cur_2,
            'Sourcemeter voltage limit:      %8.2E V' % sourcemeter_lim_vol,
            'Sourcemeter current limit:      %8.2E A' % sourcemeter_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['measurements']['IV']['delay'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]'
        ]
        #line = [biasV, vol, cur_tot, measV, volSmall, means, errs]

        hdRV = [
            'RV Sweep\n',
            'Measurement Settings:',
            'Picoammeter voltage limit:      %8.2E V' % picoammeter_lim_vol,
            'Picoammeter current limit:      %8.2E A' % picoammeter_lim_cur,
            'Picoammeter 2 voltage limit:      %8.2E V' % picoammeter_lim_vol_2,
            'Picoammeter 2 current limit:      %8.2E A' % picoammeter_lim_cur_2,
            'Sourcemeter voltage limit:      %8.2E V' % sourcemeter_lim_vol,
            'Sourcemeter current limit:      %8.2E A' % sourcemeter_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['measurements']['IV']['delay'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        return(hdIV, hdRV)
   
    def IVpoint(self, biasV):
        time.sleep(self.config['measurements']['IV']['delay'])

        cur_tot =   self.sourcemeter_1.read_current()
        vol =   self.sourcemeter_1.read_voltage()

        measurements = np.array([self.picoammeter_1.read_current() for _ in range(self.config['measurements']['IV']['sample_size'])])
        measurements_2 = np.array([self.picoammeter_2.read_current() for _ in range(self.config['measurements']['IV']['sample_size'])])
       
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['IV']['sample_size'])
        means_2 = np.mean(measurements_2, axis=0)
        errs_2 = np.std(measurements_2, axis=0)/math.sqrt(self.config['measurements']['IV']['sample_size'])

        line = [biasV, vol, cur_tot, means, errs, means_2, errs_2]
        self.logging.info("{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <8.3E}".format(*line))
        
        return(line)

    def IVscan(self, name, fig, ax2, ax3, hdIV, hdRV):

        self.logging.info('\n\nSTARTING IV SCAN...\n\n')
        self.reset_power_supplies()
        fname_out_IV = '_'.join(['iv', self.id, name]) + '.dat'
        tmp_id_y     = 'current'

        biasVs = []
        line2 = []
        I_diode = []
        I_GR = []

        try:
            # Do IV Scan
            self.sourcemeter_1.set_output_on()
            self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]')

            start_time = time.time()
            data_save = []

            for v in self.volt_list_bias_IV:
        
                self.sourcemeter_1.ramp_up(v)
                time.sleep(self.config['measurements']['IV']['delay'])

                if(not self.sourcemeter_1.check_compliance()):
                    self.logging.info('SOURCEMETER_1 HAS REACHED COMPLIANCE AT BIAS VOLTAGE: %s V', v)

                line3 = []
                Vs_amp = []
                Is_amp = []
                Is_amp2 = []
                outIV_oneBias = []
                
                lineIV = self.IVpoint(v)
                
                outIV_oneBias.append(lineIV)
                data_save.append(lineIV)

                # Recall that lineIV = [biasV, vol, cur_tot, measV, volSmall, means, errs]
                Vs_amp.append(lineIV[1])
                Is_amp.append(lineIV[3])
                Is_amp2.append(lineIV[5])
            
                biasVs.append(v)
                fname_out_IV = '_'.join(['iv', self.id, name, str(v), 'V']) + '.dat'    
                I_GR.append(Is_amp2)
                I_diode.append(Is_amp)
            
                line2 = live_plotter(biasVs, I_GR, ax2, line2, identifier="IV Curve GR", yaxis_title=tmp_id_y, color='g')
                line3 = live_plotter(biasVs, I_diode, ax3, line3, identifier="IV Curve diode pad", yaxis_title=tmp_id_y, color='g')
            

            #TODO: USE A PROFILING FUNCTION INSTEAD OF THIS MESS
            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            self.logging.info("Elapsed time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), int(seconds)))
            # --------------------------------------------------
        
        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED IN IV SCAN:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        self.reset_power_supplies()

        self.save_list(data_save, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
        self.saveSinglePlot(fig, ax2,"iv_{a}_{b}_GR.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_pad.png".format(a=self.id, b=name))

        self.logging.info('\n\n IV SCAN FINISHED\n\n')

    def execute(self):

        # Name of files
        name =  self.__class__.__name__

        # Create plots
        fig, ax3, ax2 = init_liveplot()

        ## Print header
        [hdIV, hdRV] = self.createHeader()

        self.IVscan(name, fig, ax2, ax3, hdIV, hdRV)
        
    def finalise(self):
        self._finalise()