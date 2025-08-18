import matplotlib.pyplot as plt
import matplotlib
plt.style.use('ggplot')
import time, math, os, glob, re
import numpy as np
from utils.correct_cv import lcr_series_equ, lcr_parallel_equ

# Module structure import
from measurements import measurement

def init_liveplot():
    plt.style.use('ggplot')
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

def live_plotter(x_vec, y_vec, y_err_vec, ax, identifier='', yaxis_title='', color='k', pause_time=0.1, ref_line=None):
    # Clear the axis completely on each call
    ax.clear()

    # Plot the data with error bars
    if len(x_vec) > 0:
        ax.errorbar(x_vec, y_vec, yerr=y_err_vec, fmt=color[0]+'-o', alpha=0.8, capsize=3, label=identifier)

    # Plot reference horizontal line if provided
    if ref_line is not None:
        try:
            ax.axhline(ref_line, linestyle='--', linewidth=1, label='reference C')
        except Exception:
            pass

    # Set titles and labels
    ax.set_title(identifier)
    ax.set_ylabel(yaxis_title)
    ax.set_xlabel('voltage [V]') # Standardized label
    ax.legend() # Show legend for identifier

    # Adjust plot limits dynamically
    # include reference line in limits calculation if present
    if x_vec and y_vec:
        y_all = np.array(y_vec)
        if ref_line is not None:
            y_all = np.append(y_all, ref_line)
        y_min, y_max = np.min(y_all), np.max(y_all)
        y_range = y_max - y_min if y_max > y_min else abs(y_max)
        ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

        x_min, x_max = np.min(x_vec), np.max(x_vec)
        x_range = x_max - x_min if x_max > x_min else abs(x_max)
        if x_range == 0: # Handle case where all x values are the same
            x_range = abs(x_min) if x_min != 0 else 1.0
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

        self.testset = self.config['measurements'].get('testset', [])

        # Check if dynamic voltage ranges should be used
        use_dynamic_ranges = self.config['measurements'].get('dynamic_voltage_range', {}).get('enabled', False)

        if use_dynamic_ranges:
            # Call the new function to set voltage lists dynamically
            self._calculate_dynamic_voltage_ranges()
        else:
            # Fallback to the original static range definition from config
            self.logging.info("Using static voltage ranges from config file.")
            if 'moshalf' in self.testset or 'mos2000' in self.testset:
                v_start = self.config['measurements']['CV']['range']['v_start']
                v_end = self.config['measurements']['CV']['range']['v_end']
                step = self.config['measurements']['CV']['range']['step_size']
                # Create a single CV list and assign it to both measurement types
                volt_list_cv = np.arange(v_start, v_end + step, step)
                self.volt_list_moshalf = volt_list_cv
                self.volt_list_mos2000 = volt_list_cv

            if 'gcd' in self.testset:
                v_start = self.config['measurements']['IV']['range']['v_start']
                v_end = self.config['measurements']['IV']['range']['v_end']
                step = self.config['measurements']['IV']['range']['step_size']
                self.volt_list_gcd = np.arange(v_start, v_end + step, step)

        # Common device setup
        if 'moshalf' in self.testset or 'mos2000' in self.testset:
            self.lcrmeter.set_voltage(self.config['measurements']['CV']['lcr_amplitude'])
            self.lcrmeter.set_mode('RX')


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

    def _calculate_dynamic_voltage_ranges(self):
        """
        Calculates voltage ranges based on the current dose using linear interpolation
        from empirical data. This method sets the voltage lists for each test type.
        """
        self.logging.info("Calculating dynamic voltage ranges...")

        # Empirical data: [Dose (kGy), moshalf_end, mos2000_end, gcd_end]
        empirical_data = np.array([
            [0,   -5,   -5,   -10],
            [1,   -50,  -100, -20],
            [2,   -70,  -150, -30],
            [5,   -120, -220, -35],
            [10,  -150, -280, -40],
            [20,  -180, -340, -50],
            [40,  -210, -350, -55],
            [70,  -220, -360, -65],
            [100, -220, -360, -75]
        ])

        doses = empirical_data[:, 0]
        moshalf_ranges = empirical_data[:, 1]
        mos2000_ranges = empirical_data[:, 2]
        gcd_ranges = empirical_data[:, 3]

        # Get configuration parameters from the 'dynamic_voltage_range' section
        dynamic_config = self.config['measurements']['dynamic_voltage_range']
        multiplier = dynamic_config.get('range_multiplier', 1.0) # Default to 1.0 (no change)
        size = math.floor(dynamic_config.get('voltage_array_size', 101)*multiplier)  # multiply the voltage points to avoid sparse measurement

        # Interpolate to find the end voltage for the current dose.
        # np.interp handles cases where self.current_dose is outside the range by clamping to the min/max.
        end_moshalf = np.interp(self.current_dose, doses, moshalf_ranges) * multiplier
        end_mos2000 = np.interp(self.current_dose, doses, mos2000_ranges) * multiplier
        end_gcd = np.interp(self.current_dose, doses, gcd_ranges) * multiplier
        
        self.logging.info(f"Interpolated end voltages (multiplier: {multiplier}, n_samples: {size}:")
        self.logging.info(f"  - MOShalf: {end_moshalf:.2f} V")
        self.logging.info(f"  - MOS2000: {end_mos2000:.2f} V")
        self.logging.info(f"  - GCD:     {end_gcd:.2f} V")

        # Generate the voltage arrays using np.linspace for a fixed number of points
        self.volt_list_moshalf = np.linspace(0, end_moshalf, size)
        self.volt_list_mos2000 = np.linspace(0, end_mos2000, size)
        self.volt_list_gcd = np.linspace(10, end_gcd, size) # GCD starts at +10V

    def getReferenceCapacitance(self, name):
        """
        Use the 0kGy reference file regardless of self.current_dose.
        Assumes new naming: logs/{id_with_0kGy}/.../cv_{id_with_0kGy}_{name}.dat
        """
        # ensure '0kGy' is in the id (replace any existing "<num>kGy" with "0kGy")
        id0 = self.id
        if 'kGy' in self.id:
            id0 = re.sub(r'\d+(\.\d+)?kGy', '0kGy', self.id)

        ci = 'cv' if 'MOS' in name else 'iv'
        pattern = os.path.join('logs', id0, '**', f'{ci}_{id0}_{name}.dat')
        matches = glob.glob(pattern, recursive=True)

        if not matches:
            raise FileNotFoundError(f"No reference files found for pattern: {pattern}")

        latest_file = max(matches, key=os.path.getmtime)

        with open(latest_file, 'r', encoding='utf-8') as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]

        if not lines:
            raise ValueError(f"Reference file {latest_file} is empty")

        tokens = lines[-1].split()
        if len(tokens) < 3:
            raise ValueError(f"Unexpected file format in {latest_file}; last line: '{lines[-1]}'")

        try:
            ref_cap = float(tokens[-3])
        except Exception as exc:
            raise ValueError(f"Couldn't parse capacitance from '{lines[-1]}' in {latest_file}") from exc

        self.logging.info(f"this is my reference capacitance: {ref_cap} (from {latest_file})")
        return ref_cap

    def savePlots(self, dic):
        ### Save and print
        for name,val in dic.items():
            if not val: continue # Skip if the measurement data is empty
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
                self.print_graph(np.array([v for v in val if (abs(v[0]) < 251 and abs(v[0])>-0.1)])[:, 1], \
                                 np.array([v for v in val if (abs(v[0]) < 251 and abs(v[0])>-0.1)])[:, 2], \
                                 np.array([v for v in val if (abs(v[0]) < 251 and abs(v[0])>-0.1)])[:, 3], \
                                 'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_zoom_{a}_{b}.png".format(a=self.id, b=name))
                self.print_graph(np.array(val)[:, 1], np.array(val)[:, 4], np.array(val)[:, 4]*0.01, \
                                 'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id + ' ' + name, fn="iv_total_current_{a}_{b}.png".format(a=self.id, b=name))

    def doCVScan(self, ax, name='', volt_list=None): 
        if volt_list is None or len(volt_list) == 0:
            self.logging.error(f"No voltage list provided for CV scan: {name}. Skipping.")
            return []
        

        if hasattr(self, 'switch'): self.switch.close_channel(self.config['devices']['switch']['connections'][name])
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
        tmp_id_y     = 'Capacitance [F]'
        color = 'b' if  'MOShalf' in name else 'r' if 'MOS2000' in name else 'c'
        tmp_x, tmp_y, tmp_y_err = [], [], []

        rolling_avg = []

        try:
            if self.current_dose > 0:
                reference_capacitance = self.getReferenceCapacitance(name)
            else:
                reference_capacitance = -1
            plateauVoltage = None

            # Parameters for plateau detection
            window_size = int(self.config['measurements']['CV']['plateau_window'])
            # slope tolerance is defined as 1% of the mean capacitance across the window per volt span

            ## Loop over voltages
            for cv, v in enumerate(volt_list):
                self.sourcemeter_1.ramp_voltage(v)
                time.sleep(self.config['measurements']['CV']['delay'])

                cur_tot = self.sourcemeter_1.read_current()
                vol = self.sourcemeter_1.read_voltage()

                measurements = np.array([self.lcrmeter.execute_measurement(trig_delay = self.config['measurements']['CV']['trig_delay']) for _ in range(self.config['measurements']['CV']['sample_size'])])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['CV']['sample_size'])

                r, x = means
                dr, dx = errs

                z = np.sqrt(r**2 + x**2)
                phi = np.arctan(x/r) if r != 0 else np.pi/2 * np.sign(x)
                r_s, c_s, l_s, D = lcr_series_equ(self.config['measurements']['CV']['lcr_frequency'], z, phi)
                r_p, c_p, l_p, D = lcr_parallel_equ(self.config['measurements']['CV']['lcr_frequency'], z, phi)

                dc_s = abs(c_s / x) * dx if x != 0 else 0

                line = [v, vol, self.config['measurements']['CV']['lcr_frequency'], r, dr, x, dx, c_s, c_p, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(c_s)
                tmp_y_err.append(dc_s)

                # Pass reference capacitance to the plotter so it can draw the horizontal line
                ref_line = reference_capacitance if (self.current_dose > 0 and reference_capacitance > 0) else None
                live_plotter(tmp_x, tmp_y, tmp_y_err, ax, identifier=tmp_id_title, yaxis_title=tmp_id_y, color=color, ref_line=ref_line)

                # Maintain rolling average for compatibility (not used for plateau detection anymore)
                if cv < 10:
                    rolling_avg.append(c_s)
                else:
                    rolling_avg.pop(0)
                    rolling_avg.append(c_s)

                # New plateau detection using a moving window slope + mean-within-10% of reference
                plateau_detected = False
                if self.current_dose > 0 and reference_capacitance > 0 and len(tmp_x) >= window_size:
                    try:
                        x_window = np.array(tmp_x[-window_size:])
                        y_window = np.array(tmp_y[-window_size:])
                        # Fit a linear slope to the window
                        slope, intercept = np.polyfit(x_window, y_window, 1)
                        # Voltage span across the window (avoid div by zero)
                        v_span = max(1e-6, (x_window[-1] - x_window[0]))
                        # slope tolerance: 0.5% of mean capacitance per volt across the window
                        slope_tol = (abs(np.mean(y_window)) * 0.005) / v_span

                        mean_window = np.mean(y_window)

                        is_flat_slope = abs(slope) <= slope_tol
                        is_within_ref = abs(mean_window - reference_capacitance) <= (0.10 * abs(reference_capacitance))

                        if is_flat_slope and is_within_ref:
                            plateau_detected = True
                    except Exception as ex:
                        # If polyfit fails for any reason, don't detect plateau here
                        self.logging.debug(f"Plateau detection polyfit failed: {ex}")
                        plateau_detected = False

                if plateau_detected:
                    if plateauVoltage is None:
                        plateauVoltage = v
                        self.logging.info(f"Plateau detected and voltage set to: {plateauVoltage:.2f} V")

                    # Terminate the scan if we have gone some % past the detected plateau.
                    if plateauVoltage is not None:
                        if abs(v) > abs(plateauVoltage * self.config['measurements']['CV']['plateau_extention']):
                            self.logging.info(f"Stopping measurement: |v| ({abs(v):.2f}) > {self.config['measurements']['CV']['plateau_extention']}|plateauVoltage| ({abs(plateauVoltage):.2f})")
                            break

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

    def doIVScan(self, ax, name='', volt_list=None):
        if volt_list is None or len(volt_list) == 0:
            self.logging.error(f"No voltage list provided for IV scan: {name}. Skipping.")
            return []

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
            'Voltage delay:             %8.2f s' % self.config['measurements']['IV']['delay'],
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

        self.sourcemeter_2.ramp_voltage(self.config['measurements']['IV']['gcd_diode_bias'])

        fname_out = '_'.join(['iv', self.id, name]) + '.dat'
        try:
            ## Loop over voltages
            for iv,v in enumerate(volt_list):
                self.sourcemeter_1.ramp_voltage(v)
                time.sleep(self.config['measurements']['IV']['delay'])

                cur_tot = self.sourcemeter_1.read_current()
                vol = self.sourcemeter_1.read_voltage()

                measurements = np.array([self.picoammeter.read_current() for _ in range(self.config['measurements']['IV']['sample_size'])])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)/math.sqrt(self.config['measurements']['IV']['sample_size'])

                i = means
                di = errs 

                line = [v, vol, i, di, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(i)
                tmp_y_err.append(di)

                live_plotter(tmp_x, tmp_y, tmp_y_err, ax, identifier=tmp_id_title, yaxis_title=tmp_id_y, color='g')

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
        plt.style.use('ggplot')
        self.reset_power_supplies()
        self.reset_switch()

        fig, ax0, ax1,ax2 = init_liveplot()
        plots = {}
        
        if 'moshalf' in self.testset:
            plots_cv_moshalf = self.doCVScan(ax0, name='MOShalf', volt_list=self.volt_list_moshalf)
            plots["cv_moshalf"] = plots_cv_moshalf
            self.reset_power_supplies()
            self.reset_switch()
        if 'mos2000' in self.testset:
            plots_cv_mos2000 = self.doCVScan(ax1, name='MOS2000', volt_list=self.volt_list_mos2000)
            plots["cv_mos2000"] = plots_cv_mos2000
            self.reset_power_supplies()
            self.reset_switch()
        if 'gcd' in self.testset:
            plots_iv_gcd = self.doIVScan(ax2, name='GCD', volt_list=self.volt_list_gcd)
            plots["iv_gcd"] = plots_iv_gcd
            self.reset_power_supplies()
            self.reset_switch()

        self.savePlots(plots)

    def finalise(self):
        self._finalise()
