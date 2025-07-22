import matplotlib.pyplot as plt
plt.style.use('ggplot')
import time, math
import numpy as np
import yaml
from utils.correct_cv import lcr_series_equ, lcr_parallel_equ

#TODO: move general imports to base measurement class

# Module structure import
from measurements import measurement
import devices 

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(13,13))
    ax0 = fig.add_subplot(131)
    ax1 = fig.add_subplot(132)
    ax2 = fig.add_subplot(133)
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
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
        # figManager.window.showMaximized()

    line.set_xdata(x_vec)
    line.set_ydata(y_vec)

    ax.set_ylim([np.min(y_vec)-0.005*abs(np.min(y_vec)),np.max(y_vec)+0.005*abs(np.max(y_vec))])
    ax.set_xlim([np.min(x_vec)-0.5,np.max(x_vec)+0.5])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    return line

class testEF_fullDiode(measurement): 
    
    def __init__(self, ide, config_path):
        super().__init__(ide)
        self.config_path = config_path

    def initialise(self):
        
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            self.logging.info(self.config)

        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running test: %s" % self.__class__.__name__)
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise() # base class initialisation

        self.volt_list_CV = [round(v, 1) for v in np.arange(self.config['measurements']['CV']['range']['v_start'],
                                                            self.config['measurements']['CV']['range']['v_end'] +
                                                            self.config['measurements']['CV']['range']['step_size'],
                                                            self.config['measurements']['CV']['range']['step_size'])]  # Voltage range
            

        self.sourcemeter_1 = getattr(devices, self.config['devices']['sourcemeter_1']['model'])(self.config['devices']['sourcemeter_1']['address'])
        self.switch = getattr(devices, self.config['devices']['switch']['model'])(self.config['devices']['switch']['address'])
        self.reset_switch() 
        
        self.lcrmeter = getattr(devices, self.config['devices']['lcrmeter']['model'])(self.config['devices']['lcrmeter']['address'])
        self.lcrmeter.reset()
        self.lcrmeter.set_voltage(self.config['measurements']['CV']['lcr_amplitude'])
        self.lcrmeter.set_mode(self.config['devices']['lcrmeter']['mode'])
        self.lcrmeter.set_frequency(self.config['measurements']['CV']['lcr_frequency'])

        # self.logging.info(" ----TIMER ----device init took", time.time() - self.timer, "seconds")
        self.timer = time.time()
        
    def reset_power_supplies(self):
        ## Reset power supply for CV measurement
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
        lim_vol  = self.sourcemeter_1.check_voltage_limit()
        lim_cur  = self.sourcemeter_1.check_current_limit()
        lcr_vol  = float(self.lcrmeter.check_voltage())
        lcr_freq = float(self.lcrmeter.check_frequency())

        ## Header
        hdCV = [
            'CV Sweep\n',
            'Measurement Settings:',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % float(lim_cur),
            'LCR measurement voltage:         %8.2E V' % lcr_vol,
            'LCR measurement frequency:       %8.2E Hz' % lcr_freq,
            'Voltage Delay:                   %8.2f s' % self.config['measurements']['CV']['delay'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]'
        ]


        return(hdCV)

    def CVpoint(self, biasV): 
        self.timer = time.time()

        self.sourcemeter_1.set_voltage(biasV)
        time.sleep(self.config['measurements']['CV']['delay'])

        cur_tot = self.sourcemeter_1.read_current()
        vol = self.sourcemeter_1.read_voltage()

        # self.logging.info(" ----TIMER ----reading and setting current and voltages took: ", time.time() - self.timer, "seconds")
        self.timer = time.time()

        measurements = np.array([self.lcrmeter.execute_measurement(trig_delay = self.config['measurements']['CV']['trig_delay']) for _ in range(self.config['measurements']['CV']['sample_size'])])
        # self.logging.info("Measurements: ", measurements)

        # self.logging.info(" ----TIMER ----taking measurements took:  ", time.time() - self.timer, "seconds")
        self.timer = time.time()

        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['CV']['sample_size'])



        r, x = means
        dr, dx = errs

        z = np.sqrt(r**2 + x**2)
        phi = np.arctan(x/r)
        r_s, c_s, l_s, D = lcr_series_equ(self.config['measurements']['CV']['lcr_frequency'], z, phi)
        r_p, c_p, l_p, D = lcr_parallel_equ(self.config['measurements']['CV']['lcr_frequency'], z, phi)

        line = [
            biasV,                                              # 1. The bias voltage set by the user
            vol,                                                # 2. The measured voltage from the sourcemeter
            self.config['measurements']['CV']['lcr_frequency'], # 3. The LCR meter measurement frequency
            r,                                                  # 4. Mean resistance from LCR measurements
            dr,                                                 # 5. Standard error of resistance
            x,                                                  # 6. Mean reactance from LCR measurements
            dx,                                                 # 7. Standard error of reactance
            c_s,                                                # 8. Series capacitance (from LCR series equivalent)
            c_p,                                                # 9. Parallel capacitance (from LCR parallel equivalent)
            cur_tot                                             # 10. Total current measured by the sourcemeter
        ]
        
        self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        # self.logging.info(" ----TIMER ----computing and logging line took:  ", time.time() - self.timer, "seconds")
        self.timer = time.time()

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

        self.sourcemeter_1.set_output_on()


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
                line = live_plotter(biasVs, 1/(np.abs(np.array(Cs_LCR))-self.config['devices']['lcrmeter']['approx_open_corr'])**2, ax0, line, identifier=label, yaxis_title='1/Cs^2 [F^-2]', color=color)           

                # self.logging.info(" ----TIMER ----parsing line after CVpoint took:  ", time.time() - self.timer, "seconds")
                self.timer = time.time()     


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
        name =  self.__class__.__name__

        # Create plots
        fig, ax0, ax1, ax2 = init_liveplot()

        ## Print header
        hdCV = self.createHeader()
        for line in hdCV:
            self.logging.info(line)

        self.testset = self.config['measurements'].get('testset', []) 

        if 'floating' in self.testset:
            self.CVscan(name, fig, ax0, hdCV)
        if 'short' in self.testset:
            self.CVscan(name, fig, ax1, hdCV, shortGR=True)
        if 'ground' in self.testset:
            self.CVscan(name, fig, ax2, hdCV, groundGR=True)

    def finalise(self):
        self._finalise()