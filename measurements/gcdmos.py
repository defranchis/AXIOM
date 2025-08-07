import matplotlib.pyplot as plt
import matplotlib
plt.style.use('ggplot')
import time, math, os
import numpy as np
from utils.correct_cv import lcr_series_equ, lcr_parallel_equ

# Module structure import
from measurements import measurement

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(15,5))
    ax0 = fig.add_subplot(131)
    ax1 = fig.add_subplot(132)
    ax2 = fig.add_subplot(133)
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
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

def live_plotter(x_vec, y_vec, y_err_vec, ax, identifier='', yaxis_title='', color='k',pause_time=0.1):
    # Clear the axis completely on each call
    ax.clear()

    # Plot the data with error bars
    ax.errorbar(x_vec, y_vec, yerr=y_err_vec, fmt=color[0]+'-o', alpha=0.8, capsize=3, label=identifier)

    # Set titles and labels
    ax.set_title(identifier)
    ax.set_ylabel(yaxis_title)
    ax.set_xlabel('voltage [V]') # Standardized label
    ax.legend() # Show legend for identifier

    # Adjust plot limits dynamically
    if x_vec and y_vec:
        y_min, y_max = np.min(y_vec), np.max(y_vec)
        y_range = y_max - y_min if y_max > y_min else abs(y_max)
        ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

        x_min, x_max = np.min(x_vec), np.max(x_vec)
        x_range = x_max - x_min if x_max > x_min else abs(x_max)
        ax.set_xlim(x_min - 0.1 * x_range, x_max + 0.1 * x_range)

    # This pauses the data so the figure/axis can catch up
    plt.pause(pause_time)

    # No need to return a line object
    return None

class gcdmos(measurement):

    def __init__(self, config=None, current_dose=None, n_annealing = None, **kwargs):
        super().__init__(config=config, current_dose=current_dose, n_annealing=n_annealing)


    def initialise(self):
        self._initialise()
        self._initialise_devices()

        self.testset = self.config['measurements'].get('testset', [])  #to detemrine which tests to run and which devices to initialize. 

        if 'moshalf' in self.testset or 'mos2000' in self.testset:
            self.volt_list_cv = np.arange(
                self.config['measurements']['CV']['range']['v_start'],
                self.config['measurements']['CV']['range']['v_end'] + self.config['measurements']['CV']['range']['step_size'],
                self.config['measurements']['CV']['range']['step_size']
            )
            self.lcrmeter.set_voltage(self.config['measurements']['CV']['lcr_amplitude'])
            self.lcrmeter.set_mode('RX')
        
        if 'gcd' in self.testset:
            # IV measurement voltage list
            self.volt_list_iv = np.arange(
                self.config['measurements']['IV']['range']['v_start'],
                self.config['measurements']['IV']['range']['v_end'] +  self.config['measurements']['IV']['range']['step_size'],
                self.config['measurements']['IV']['range']['step_size']
            )


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
        # MARC keithley2410.set_interlock_on()
        self.sourcemeter_1.set_output_off()
        time.sleep(1)

        if 'gcd' in self.testset:
            ## Reset power supply of the second keithley which biases the gcd diode
            self.sourcemeter_2.ramp_voltage(0)
            self.sourcemeter_2.set_output_off()
            self.sourcemeter_2.reset()
            self.sourcemeter_2.set_source('voltage')
            self.sourcemeter_2.set_sense('current')
            self.sourcemeter_2.set_current_limit(self.config['devices']['sourcemeter_1']['lim_cur'])
            self.sourcemeter_2.set_voltage(0)
            self.sourcemeter_2.set_terminal('rear')
            self.sourcemeter_2.set_output_off()
            time.sleep(1)

            self.picoammeter.reset()
            self.picoammeter.setup_ammeter()
            self.picoammeter.set_nplc(2)
            self.picoammeter.set_range(self.config['devices']['picoammeter']['lim_cur'])

    def reset_switch(self):
        # only reset switch if actually used in current configuration
        if hasattr(self, 'switch'): 
            self.switch.reset(1)
            self.switch.get_idn()
            self.switch.open_all()
    
    #TODO: refactor, this is consolidation of concerns. refactor or potentially remove scanning behaviour 
    def getReferenceCapacitance(self, name):
        elms = self.id.split('_')
        newelms = []
        for e in elms:
            if 'kGy'in e:
                newelms.append('0kGy')
            elif 'annealing' in e:
                continue
            else:
                newelms.append(e)

        basename = '_'.join(newelms)

        basefilename = '{ci}_{bn}_{name}.dat'.format(bn=basename, ci = 'cv' if 'MOS' in name else 'iv', name=name)

        allbasefiles = []

        for root, dirs, files in os.walk("logs/"+basename+"/", topdown = False):
            for name in files:
                if basefilename in os.path.join(root,name):
                    self.logging.info('found the reference file for capacistances: '+str(os.path.join(root, name)))
                    allbasefiles.append(os.path.join(root, name))

        allbasefiles = sorted(allbasefiles)

        f = open( allbasefiles[-1], 'r')
        f_l = f.readlines()
        ref_cap = float(f_l[-1].split()[-3])
        self.logging.info('this is my reference capacitance: '+str(ref_cap))
        f.close()

        return ref_cap
        
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

    def doCVScan(self, ax, name=''): 


        if hasattr(self, 'switch'): self.switch.close_channel(self.config['devices']['switch']['connections']['lcrmeter'])
        self.sourcemeter_1.set_output_on()

        lim_vol  = self.sourcemeter_1.check_voltage_limit()
        lim_cur  = self.sourcemeter_1.check_current_limit()
        lcr_vol  = float(self.lcrmeter.check_voltage())
        lcr_freq = float(self.lcrmeter.check_frequency())
        hd = [
            'Single CV\n',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % float(lim_cur),
            'LCR measurement voltage:         %8.2E V' % lcr_vol,
            'LCR measurement frequency:       %8.2E Hz' % lcr_freq,
            'Voltage Delay:                   %8.2f s' % self.config['measurements']['CV']['delay'],
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]'
        ]
        for line in hd[1:-2]: self.logging.info(line)
        self.logging.info("\t\n\t" + hd[-1] + "\n" + "-" * int(1.2 * len(hd[-1])))

        ## Prepare
        out = []

        ## for plotting
        tmp_id_title = 'CV '+ name+ ': ' + self.id.replace('_m',' -').replace('_p',' +').replace('_',' ')
        tmp_id_y     = 'Capacitance [F]' # More specific y-axis title
        color = 'b' if  'MOShalf' in name else 'r' if 'MOS2000' in name else 'c'
        tmp_x, tmp_y, tmp_y_err = [], [], [] # Add list for y-errors

        c_baseline = 0.
        rolling_avg = []

        try:
            if not self.config['sample']['preirradiated']:
                reference_capacitance = self.getReferenceCapacitance(name)
            else:
                reference_capacitance = -1
            plateauVoltage = 999.
            ## Loop over voltages
            for cv, v in enumerate(self.volt_list_cv):
                self.sourcemeter_1.ramp_voltage(v)
                time.sleep(self.config['measurements']['CV']['delay'])

                cur_tot = self.sourcemeter_1.read_current()
                vol = self.sourcemeter_1.read_voltage()

                measurements = np.array([self.lcrmeter.execute_measurement() for _ in range(self.config['measurements']['CV']['sample_size'])])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['CV']['sample_size'])

                r, x = means
                dr, dx = errs

                z = np.sqrt(r**2 + x**2)
                phi = np.arctan(x/r)
                r_s, c_s, l_s, D = lcr_series_equ(self.config['measurements']['CV']['lcr_frequency'], z, phi)
                r_p, c_p, l_p, D = lcr_parallel_equ(self.config['measurements']['CV']['lcr_frequency'], z, phi)

                # --- Calculate the error on Cs ---
                dc_s = abs(c_s / x) * dx if x != 0 else 0

                line = [v, vol, self.config['measurements']['CV']['lcr_frequency'], r, dr, x, dx, c_s, c_p, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(c_s)
                tmp_y_err.append(dc_s) # Store the error

                ## update the live plotting
                live_plotter(tmp_x, tmp_y, tmp_y_err, ax, identifier=tmp_id_title, yaxis_title=tmp_id_y, color=color)

                if cv < 10:
                    c_baseline = c_baseline + (c_s - c_baseline)/(cv+1)
                    rolling_avg.append(c_s)
                else:
                    rolling_avg.pop(0)
                    rolling_avg.append(c_s)
                curr_avg = np.mean(rolling_avg)
                rms = math.sqrt(sum([i**2 for i in rolling_avg])/len(rolling_avg))
                if c_s > 0.9*reference_capacitance and not self.config['sample']['preirradiated']:
                    print('this is the rms of the last 10', rms)
                    if 0.985*rms < c_s < 1.015*rms:
                        self.logging.info('it looks like the plateau is reached... ending measurement!')
                        if plateauVoltage > 0: plateauVoltage = v
                        if not self.config['sample']['preirradiated'] and v < 1.2*plateauVoltage:
                            break
                        else:
                            self.logging.info('going on because this is a preirradiated sample or we want to go the extra mile...')


        except BaseException as e:
            self.logging.info('EXCEPTION RAISED:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        ## Save and print
        fname_out = '_'.join(['cv', self.id, name]) + '.dat'
        self.logging.info("\n")
        self.save_list(out, fname_out, fmt="%.5E", header="\n".join(hd))

        return out
        ## end of CV scan

    def doIVScan(self, ax, name=''):

        if hasattr(self, 'switch'): self.switch.close_channel(self.config['devices']['switch']['connections']['picoammeter'])
        self.sourcemeter_1.set_output_on()
        self.sourcemeter_2.set_output_on()

        ke6487_lim_vol = -999.
        ke6487_lim_cur = self.config['devices']['picoammeter']['lim_cur']
        ke2410_lim_vol  = self.sourcemeter_1.check_voltage_limit()
        ke2410_lim_cur  = self.sourcemeter_1.check_current_limit()
        hd = [
            'Single IV\n',
            'Measurement Settings:',
            'Ke6487 voltage limit:      %8.2E V' % ke6487_lim_vol,
            'Ke6487 current limit:      %8.2E A' % ke6487_lim_cur,
            'Ke2410 voltage limit:      %8.2E V' % ke2410_lim_vol,
            'Ke2410 current limit:      %8.2E A' % ke2410_lim_cur,
            'Voltage delay:                   %8.2f s' % self.config['measurements']['IV']['delay'],
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]
        for line in hd[1:-2]: self.logging.info(line)
        self.logging.info("\t\n\t" + hd[-1] + "\n" + "-" * int(1.2 * len(hd[-1])))

        ## Prepare
        out = []

        ## for plotting
        tmp_id_title = 'IV '+ name+ ': ' + self.id.replace('_m',' -').replace('_p', ' +').replace('_',' ')
        tmp_id_y     = 'Current [A]' # More specific y-axis title
        color = 'g'
        tmp_x, tmp_y, tmp_y_err = [], [], [] # Add list for y-errors

        self.sourcemeter_2.ramp_voltage(1*self.config['measurements']['IV']['gcd_diode_bias'])

        cutOffVoltage = -85

        if self.current_dose <=1: cutOffVoltage = -30
        elif self.current_dose <=2: cutOffVoltage = -40 
        elif self.current_dose <=5: cutOffVoltage = -55 
        elif self.current_dose <=10: cutOffVoltage = -65 
        elif self.current_dose <=20: cutOffVoltage = -70 
        elif self.current_dose <=40: cutOffVoltage = -75 

        print('cut-off voltage = {} V'.format(cutOffVoltage))

        fname_out = '_'.join(['iv', self.id, name]) + '.dat'
        i_baseline, stddev, spread = 0., 0., 0.
        rolling_avg, rolling_avgs = [], []
        nowBelow = False
        minCurrent = 100000.
        crossOver = 9999
        try:
            ## Loop over voltages
            for iv,v in enumerate(self.volt_list_iv):
                if v < cutOffVoltage:
                    break
                self.sourcemeter_1.ramp_voltage(v)
                time.sleep(self.config['measurements']['IV']['delay'])

                cur_tot = self.sourcemeter_1.read_current()
                vol = self.sourcemeter_1.read_voltage()

                measurements = np.array([self.picoammeter.read_current() for _ in range(self.config['measurements']['IV']['sample_size'])])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['IV']['sample_size'])

                i = means
                di = errs 

                if i < minCurrent:
                    minCurrent = i

                line = [v, vol, i, di, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(i)
                tmp_y_err.append(di) # Store the error

                ## update the live plotting
                live_plotter(tmp_x, tmp_y, tmp_y_err, ax, identifier=tmp_id_title, yaxis_title=tmp_id_y, color='g')

                nFirst = 15 if not self.config['sample']['preirradiated'] else 5
                if iv and iv < nFirst:
                    i_baseline = i_baseline + (i - i_baseline)/(iv)
                    rolling_avg.append(i)
                    stddev = np.std(rolling_avg)
                    spread = abs(max(rolling_avg)-min(rolling_avg))
                elif iv >=nFirst:
                    rolling_avg.pop(0)
                    rolling_avg.append(i)
                if iv > 3: rolling_avgs.append(tmp_y[-3:])
                curr_avg = np.mean(rolling_avg) if iv else 0.
                print('i baseline: {b:.3f}'.format(b=float(i_baseline*1e10)))
                print('current average and spread: {a:.3f} +- {b:.3f}'.format(a=float(curr_avg*1e10), b=float(spread*1e10)))
                if not nowBelow and iv > 9 and i < (i_baseline-5.*spread):
                    nowBelow = True
                    self.logging.info('IV scan: i have now reached the bottom of the well!!!!')
                    crossOver = v
                if i > self.config['devices']['picoammeter']['lim_cur']:
                    self.logging.info('reached compliance in the keithley6487')
                    self.reset_power_supplies()
                    break

        except BaseException as e:
            self.logging.info('EXCEPTION RAISED:', e)
            self.logging.error("EXCEPTION RAISED. Ramping down voltage and shutting down.\n")
            self.logging.error(e)
            pass

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, fname_out, fmt="%.5E", header="\n".join(hd))

        return out

    def execute(self):

        self.reset_power_supplies()
        self.reset_switch()

        fig, ax0, ax1,ax2 = init_liveplot()
        plots = {}
        
        if 'moshalf' in self.testset:
            plots_cv_moshalf = self.doCVScan(ax0, name='MOShalf')
            plots["cv_moshalf"] = plots_cv_moshalf
            self.reset_power_supplies()
            self.reset_switch()
        if 'mos2000' in self.testset:
            plots_cv_mos2000 = self.doCVScan(ax1, name='MOS2000')
            plots["cv_mos2000"] = plots_cv_mos2000
            self.reset_power_supplies()
            self.reset_switch()
        if 'gcd' in self.testset:
            plots_iv_gcd = self.doIVScan(ax2, name='GCD')
            plots["iv_gcd"] = plots_iv_gcd
            self.reset_power_supplies()
            self.reset_switch()

        self.savePlots(plots)

    def finalise(self):
        self._finalise()
