import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import subplots, savefig
from matplotlib.ticker import AutoMinorLocator, MaxNLocator
plt.style.use('ggplot')
import time, math
import numpy as np
import yaml
from utils.correct_cv import lcr_series_equ, lcr_parallel_equ


from measurements import measurement
import devices



def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(13,13))
    ax0 = fig.add_subplot(241)
    ax1 = fig.add_subplot(245)
    ax2 = fig.add_subplot(244)
    ax3 = fig.add_subplot(248)
    ax4 = fig.add_subplot(242)
    ax5 = fig.add_subplot(246)
    ax6 = fig.add_subplot(243)
    ax7 = fig.add_subplot(247)


    return fig, ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7

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

## TODO this should probably be refactored due to the amount of internally defined functions
class testMD_fullStrip(measurement):

    def __init__(self, ide, config_path):
        super().__init__(ide)    
        self.config_path = config_path 

    def initialise(self):

        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            print(self.config)

        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running test: %s" % self.__class__.__name__)
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        # CV measurement voltage list from config
        self.volt_list_bias_CV = np.arange(
            self.config['measurements']['CV']['range']['v_min'],
            self.config['measurements']['CV']['range']['v_max'] + self.config['measurements']['CV']['range']['step_size'],
            self.config['measurements']['CV']['range']['step_size']
        )

        # IV measurement voltage list
        self.volt_list_iv = np.arange(
            self.config['measurements']['IV']['measurement_range']['v_min'],
            self.config['measurements']['IV']['measurement_range']['v_max'] +  self.config['measurements']['IV']['measurement_range']['step_size'],
            self.config['measurements']['IV']['measurement_range']['step_size']
        )

        # IV bias voltage list
        self.volt_list_bias_IV = np.arange(
            self.config['measurements']['IV']['bias_range']['v_min'],
            self.config['measurements']['IV']['bias_range']['v_max'] + self.config['measurements']['IV']['bias_range']['step_size'],
            self.config['measurements']['IV']['bias_range']['step_size']
        )

        self.sourcemeter_1 = getattr(devices, self.config['devices']['sourcemeter_1']['model'])(self.config['devices']['sourcemeter_1']['address'])
        self.sourcemeter_2 = getattr(devices, self.config['devices']['sourcemeter_2']['model'])(self.config['devices']['sourcemeter_2']['address'])

        self.switch =  getattr(devices, self.config['devices']['switch']['model'])(self.config['devices']['switch']['address'])
        self.reset_switch()

        ## Set up lcr meter
        self.lcrmeter =  getattr(devices, self.config['devices']['lcrmeter']['model'])(self.config['devices']['lcrmeter']['address'])
        self.lcrmeter.reset()
        self.lcrmeter.set_voltage(self.config['measurements']['CV']['lcr_amplitude'])
        self.lcrmeter.set_mode('RX')

        self.picoammeter =  getattr(devices, self.config['devices']['picoammeter']['model'])(self.config['devices']['picoammeter']['address'])

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
        

        ## Reset power supply of the second keithley which biases the gcd diode
        #self.sourcemeter_1_gcddiode.ramp_voltage(0)
        #self.sourcemeter_1_gcddiode.set_output_off()
        #self.sourcemeter_1_gcddiode.reset()
        #self.sourcemeter_1_gcddiode.set_source('voltage')
        #self.sourcemeter_1_gcddiode.set_sense('current')
        #self.sourcemeter_1_gcddiode.set_current_limit(self.config['devices']['sourcemeter_1']['lim_cur'])
        #self.sourcemeter_1_gcddiode.set_voltage(0)
        #self.sourcemeter_1_gcddiode.set_terminal('rear')
        # MARC keithley2410_gcddiode.set_interlock_on()
        #self.sourcemeter_1_gcddiode.set_output_off()
        #time.sleep(1)

        self.picoammeter.ramp_down()
        self.picoammeter.reset()
        self.picoammeter.setup_ammeter()
        self.picoammeter.set_nplc(2)
        #self.picoammeter.set_range(self.lim_cur_ke6487)

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
        lim_vol  = self.sourcemeter_1.check_voltage_limit()
        lim_cur  = self.sourcemeter_1.check_current_limit()
        lcr_vol  = float(self.lcrmeter.check_voltage())
        lcr_freq = float(self.lcrmeter.check_frequency())

        # IV
        ke6487_lim_vol = -999. #self.picoammeter.check_voltage_limit()
        #ke6487_lim_cur = self.lim_cur_ke6487 ## hopefully keithley6487.check_current_limit() #self.picoammeter.check_current_limit()
        ke2410_lim_vol  = self.sourcemeter_2.check_voltage_limit()
        ke2410_lim_cur  = self.sourcemeter_2.check_current_limit()

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

        hdIV = [
            'IV Sweep\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            #'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['measurements']['IV']['delay'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]'
        ]
        #line = [biasV, vol, cur_tot, measV, volSmall, means, errs]

        hdRV = [
            'RV Sweep\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            #'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['measurements']['IV']['delay'],
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        return(hdCV, hdIV, hdRV)

    def CVpoint(self, biasV, freq, channel): 

        self.switch.close_channel(channel)
        self.sourcemeter_1.set_output_on()
        self.sourcemeter_1.ramp_up(biasV)
        self.sourcemeter_2.set_output_on()  #TODO: WHY IS THE SECOND SOURCEMETER USED ONLY HERE TO DO NOTHING?
        self.sourcemeter_2.ramp_up(0)
        time.sleep(self.config['measurements']['CV']['delay'])

        cur_tot = self.sourcemeter_1.read_current()
        vol = self.sourcemeter_1.read_voltage()

        print("New frequency:", freq)
        self.lcrmeter.set_frequency(freq)
        time.sleep(1)

        measurements = np.array([self.lcrmeter.execute_measurement() for _ in range(self.config['measurements']['CV']['sample_size'])])
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['CV']['sample_size'])

        r, x = means
        dr, dx = errs

        z = np.sqrt(r**2 + x**2)
        phi = np.arctan(x/r)
        print({'freq': freq, 'z': z, 'phi': phi})
        r_s, c_s, l_s, D = lcr_series_equ(freq, z, phi)
        r_p, c_p, l_p, D = lcr_parallel_equ(freq, z, phi)

        line = [biasV, vol, freq, r, dr, x, dx, c_s, c_p, cur_tot]
        
        self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        return (line)
        ## end of CV scan

    def IVpoint(self, biasV, measV):
        self.sourcemeter_2.ramp_voltage(measV)
        time.sleep(self.config['measurements']['IV']['step_delay'])

        cur_tot = self.sourcemeter_1.read_current()
        vol = self.sourcemeter_1.read_voltage()
        cur_totSmall = self.sourcemeter_2.read_current()
        volSmall = self.sourcemeter_2.read_voltage()

        measurements = np.array([self.picoammeter.read_current() for _ in range(self.config['measurements']['IV']['sample_size'])])
        #measurements = measurements[2*self.config['measurements']['IV']['sample_size']:]
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['IV']['sample_size'])

        #TODO V bias set, V bias measured, I bias, V ramp set, V ramp meas, I ramp, I amm, err I amm
        line = [biasV, vol, cur_tot, measV, volSmall, means, errs, cur_totSmall]
        self.logging.info("{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <8.3E}\t{: <8.3E}".format(*line))

        #if means > self.lim_cur_ke6487:
        #    self.logging.info('reached compliance in the keithley6487')
        #    raise Exception("Reached compliance in the keithley6487")
        
        return(line)

    def retrieveR(self, V, I):

        # That 3 is making linear regression from 3V to 5V
        #index_3V = min(range(len(V)), key=lambda i: abs(V[i]-3))
        #G, Iq = np.polyfit(V[index_3V:], I[index_3V:], 1)
        G, Iq = np.polyfit(V, I, 1)
        return (1/G, Iq)

    def CVscan(self, name, fig, ax0, ax1, ax4, ax5, ax6, ax7, hdCV):

        self.logging.info('\n\nSTARTING CV SCAN...\n\n')
        fname_out_CV = '_'.join(['cv', self.id, name]) + '.dat'

        biasVsa = []#np.empty((len(self.volt_list_bias_CV), len(self.config['measurements']['CV']['frequencies'])))
        Rs_LCRa = []#np.empty((len(self.volt_list_bias_CV), len(self.config['measurements']['CV']['frequencies'])))
        Cs_LCRa = []#np.empty((len(self.volt_list_bias_CV), len(self.config['measurements']['CV']['frequencies'])))

        biasVsb = []
        Rs_LCRb = []
        Cs_LCRb = []

        biasVsc = []
        Rs_LCRc = []
        Cs_LCRc = []

        line0a = []
        line1a = []
        line0b = []
        line1b = []
        line0c = []
        line1c = []

        outCVa = []
        outCVb = []
        outCVc = []
        
        colora = 'b'
        colorb = 'r'
        colorc = 'g'
        tmp_id_y_R     = r'$R$'
        tmp_id_y_C     = r'$C$'


        self.reset_power_supplies()
        self.reset_switch()


         # Do CV Scan
        try:            

            #TODO: improve this for loop to use the same code for all frequencies (iterating over the frequencies and then comparing to the same list is unhinged)
            self.logging.info("Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]")
            for v in self.volt_list_bias_CV:
                for f in self.config['measurements']['CV']['frequencies']:
                    lineCV = self.CVpoint(v, f, 1)
                    
                    # Recall that lineCV = [biasV, vol, self.config['measurements']['CV']['frequencies'], r, dr, x, dx, c_s, c_p, cur_tot]
                    #biasVs[self.volt_list_bias_CV.index(v), self.config['measurements']['CV']['frequencies'].index(f)] = lineCV[0]
                    #Rs_LCR[self.volt_list_bias_CV.index(v), self.config['measurements']['CV']['frequencies'].index(f)] = lineCV[3]
                    #Cs_LCR[self.volt_list_bias_CV.index(v), self.config['measurements']['CV']['frequencies'].index(f)] = lineCV[8]
                    
                    if f == self.config['measurements']['CV']['frequencies'][0]:
                        outCVa.append(lineCV)
                        biasVsa.append(lineCV[0])
                        Rs_LCRa.append(lineCV[3])
                        Cs_LCRa.append(lineCV[8])
                        line0a = live_plotter(biasVsa, Rs_LCRa, ax0, line0a, identifier=f"RV curve (LCR) {f:.0f}Hz", yaxis_title=tmp_id_y_R, color=colora)
                        line1a = live_plotter(biasVsa, Cs_LCRa, ax1, line1a, identifier=f"CV curve {f:.0f}Hz", yaxis_title=tmp_id_y_C, color=colora)
                    if f == self.config['measurements']['CV']['frequencies'][1]:
                        outCVb.append(lineCV)
                        biasVsb.append(lineCV[0])
                        Rs_LCRb.append(lineCV[3])
                        Cs_LCRb.append(lineCV[8])
                        line0b = live_plotter(biasVsb, Rs_LCRb, ax4, line0b, identifier=f"RV curve (LCR) {f:.0f}Hz", yaxis_title=tmp_id_y_R, color=colorb)
                        line1b = live_plotter(biasVsb, Cs_LCRb, ax5, line1b, identifier=f"CV curve {f:.0f}Hz", yaxis_title=tmp_id_y_C, color=colorb)
                    if f == self.config['measurements']['CV']['frequencies'][2]:
                        outCVc.append(lineCV)
                        biasVsc.append(lineCV[0])
                        Rs_LCRc.append(lineCV[3])
                        Cs_LCRc.append(lineCV[8])
                        line0c = live_plotter(
                            biasVsc, Rs_LCRc, ax6, line0c,
                            identifier=f"RV curve (LCR) {f:.0f}Hz", yaxis_title=tmp_id_y_R, color=colorc
                        )
                        line1c = live_plotter(biasVsc, Cs_LCRc, ax7, line1c, identifier=f"CV curve {f:.0f}Hz", yaxis_title=tmp_id_y_C, color=colorc)
                    #line0[:,self.config['measurements']['CV']['frequencies'].index(f)] = live_plotter(biasVs[:, self.config['measurements']['CV']['frequencies'].index(f)], Rs_LCR[:, self.config['measurements']['CV']['frequencies'].index(f)], ax0, line0[:,self.config['measurements']['CV']['frequencies'].index(f)], identifier="RV curve (LCR)", yaxis_title=tmp_id_y_R, color=color)
                    #line1[:,self.config['measurements']['CV']['frequencies'].index(f)] = live_plotter(biasVs[:, self.config['measurements']['CV']['frequencies'].index(f)], Cs_LCR[:, self.config['measurements']['CV']['frequencies'].index(f)], ax1, line1[:,self.config['measurements']['CV']['frequencies'].index(f)], identifier="CV curve", yaxis_title=tmp_id_y_C, color=color)
                


        except BaseException as e: #KeyboardInterrupt:
            self.logging.info('EXCEPTION RAISED IN CV SCAN:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        self.reset_power_supplies()
        self.reset_switch()

        self.saveSinglePlot(fig, ax1,"10KHz_cv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax0,"10KHz_rv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax5,"100KHz_cv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax4,"100KHz_rv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax7,"1MHz_cv_LCR_{a}_{b}.png".format(a=self.id, b=name))
        self.saveSinglePlot(fig, ax6,"1MHz_rv_LCR_{a}_{b}.png".format(a=self.id, b=name))


        self.save_list(outCVa, "10KHz_"+fname_out_CV, fmt="%.5E", header="\n".join(hdCV))
        self.save_list(outCVb, "100KHz_"+fname_out_CV, fmt="%.5E", header="\n".join(hdCV))
        self.save_list(outCVc, "1MHz_"+fname_out_CV, fmt="%.5E", header="\n".join(hdCV))

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
            self.sourcemeter_1.set_output_on()
        
            #self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t')
            self.logging.info('Nominal Voltage [V]\t Measured Voltage [V]\tTotal current [A]\tIS nominal voltage[V]\tIS measured voltage[V]\tIS current [A]\tIS current Error [A]\tRamping PS current[A]')

            for i, v in enumerate(self.volt_list_bias_IV):

                start_time = time.time()
                
                self.sourcemeter_1.ramp_up(v)
                # time.sleep(self.config['measurements']['IV']['delay'])
                self.sourcemeter_2.set_output_on()
                time.sleep(self.config['measurements']['IV']['delay'])


                    

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
                    line3 = live_plotter(
                        Vs_amp, Is_amp, ax3, line3,
                        identifier=f"IV Curve (Bias {v} V)", yaxis_title=tmp_id_y, color='g'
                    )
            
                self.sourcemeter_2.ramp_down_slow()
                # time.sleep(self.config['measurements']['IV']['step_delay'])
                self.sourcemeter_2.set_output_off()
                biasVs.append(v)
                fname_out_IV = '_'.join(['iv', self.id, name, str(v), 'V']) + '.dat'    
                self.save_list(outIV_oneBias, fname_out_IV, fmt="%.5E", header="\n".join(hdIV))
                self.saveSinglePlot(fig, ax3,"iv_{a}_{b}_{c}.png".format(a=self.id, b=name, c=v))

                [R_amp, Iq_amp] = self.retrieveR(Vs_amp, Is_amp)
                outRV.append([v, R_amp])
                Rs_amp.append(R_amp)
            
                line2 = live_plotter(biasVs, Rs_amp, ax2, line2, identifier="RV Curve (Amp)", yaxis_title=tmp_id_y_R, color='r')

                elapsed_time = time.time() - start_time
                self.logging.info("Elapsed time:")
                self.logging.info(elapsed_time)
        
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
        name =  self.__class__.__name__

        ##Create plots
        fig, ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7 = init_liveplot()

        ## Print header
        [hdCV, hdIV, hdRV] = self.createHeader()
        for line in hdCV:
            self.logging.info(line)

        self.CVscan(name, fig, ax0, ax1, ax4, ax5, ax6, ax7, hdCV)
        # print("-------------------------------------------------------------------------------")
        # print("---------------- CURRENTLY ONLY RUNNING THE IV MEASUREMENTS -------------------")
        # print("-------------------------------------------------------------------------------")
        self.IVscan(name, fig, ax2, ax3, hdIV, hdRV)
   
    def finalise(self):
        self._finalise()