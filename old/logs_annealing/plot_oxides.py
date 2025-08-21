import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
import numpy as np
from scipy import stats

cmap = plt.get_cmap('plasma')

def parse_datetime(folder_name):
    match = re.search(r'(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})', folder_name)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d-%H-%M-%S')
    return None

def extract_sensor_name(folder_name):
    parts = folder_name.split('_')
    id = parts[2]
    thickness = parts[3]
    return thickness+" ("+id+")"

def read_data_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        header = next(line for line in lines if not line.startswith('#')).strip()
        columns = next((line.lstrip('# ').strip() for line in reversed(lines) if line.startswith('#')), None)
        data = [line.strip() for line in lines if not line.startswith('#') and line.strip()]
    
    df = pd.DataFrame([row.split('\t') for row in data], columns=columns.split('\t'))
    return df

def process_cv_file(file_path):
    try:
        df = read_data_file(file_path)
        df['Nominal Voltage [V]'] = df['Nominal Voltage [V]'].astype(float)
        df['Cs [F]'] = df['Cs [F]'].astype(float)
        return df[['Nominal Voltage [V]', 'Cs [F]']]
    except Exception as e:
        print(f"Error processing CV file {file_path}: {str(e)}")
        return None

def process_iv_file(file_path):
    try:
        df = read_data_file(file_path)
        voltage = df['IS measured voltage[V]'].astype(float)
        current = df['IS current [A]'].astype(float)
        current_error = df['IS current Error [A]'].astype(float)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(voltage, current)
        
        resistance = 1 / slope if slope != 0 else float('inf')
        resistance_error = abs(resistance**2 * std_err)
        
        nominal_voltage = float(df['Nominal Voltage [V]'].iloc[0])
        return nominal_voltage, resistance, resistance_error
    except Exception as e:
        print(f"Error processing IV file {file_path}: {str(e)}")
        return None, None, None

def filter_outliers(data, threshold=10):
    filtered_data = []
    for i in range(len(data)):
        if i == 0 or i == len(data) - 1:
            filtered_data.append(data[i])
        else:
            prev_value = data[i-1][1]
            current_value = data[i][1]
            next_value = data[i+1][1]
            if (current_value < threshold * prev_value and 
                current_value < threshold * next_value):
                filtered_data.append(data[i])
    return filtered_data

def analyze_sensor_data(data_dir):
    voltage_data = {'capacitance': {}, 'resistance': {}}

    for root, dirs, files in os.walk(data_dir):
        for dir in dirs:
            if 'm20C' in dir:
                folder_path = os.path.join(root, dir)
                datetime_obj = parse_datetime(dir)
                sensor_name = extract_sensor_name(dir)

                for subdir, _, subfiles in os.walk(folder_path):
                    dat_files = [f for f in subfiles if f.endswith('.dat')]
                    cv_file = next((f for f in dat_files if f.startswith('10KHz_cv_')), None)
                    iv_files = [f for f in dat_files if f.startswith('iv_')]

                    if cv_file:
                        cv_data = process_cv_file(os.path.join(subdir, cv_file))
                        if cv_data is not None:
                            for _, row in cv_data.iterrows():
                                voltage = row['Nominal Voltage [V]']
                                capacitance = row['Cs [F]']
                                if voltage not in voltage_data['capacitance']:
                                    voltage_data['capacitance'][voltage] = {}
                                if sensor_name not in voltage_data['capacitance'][voltage]:
                                    voltage_data['capacitance'][voltage][sensor_name] = []
                                voltage_data['capacitance'][voltage][sensor_name].append((datetime_obj, capacitance))

                    for iv_file in iv_files:
                        nominal_voltage, resistance, resistance_error = process_iv_file(os.path.join(subdir, iv_file))
                        if nominal_voltage is not None and resistance is not None:
                            if nominal_voltage not in voltage_data['resistance']:
                                voltage_data['resistance'][nominal_voltage] = {}
                            if sensor_name not in voltage_data['resistance'][nominal_voltage]:
                                voltage_data['resistance'][nominal_voltage][sensor_name] = []
                            voltage_data['resistance'][nominal_voltage][sensor_name].append((datetime_obj, resistance, resistance_error))

    return voltage_data

def plot_voltage_data(voltage_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Plot capacitance
    for voltage, sensor_data in voltage_data['capacitance'].items():
        plt.figure(figsize=(12, 6))
        for index, (sensor_name, measurements) in enumerate(sensor_data.items()):
            if measurements:
                filtered_measurements = filter_outliers(measurements)
                dates, capacitances = zip(*filtered_measurements)
                start_date = min(dates)
                days = [(date - start_date).total_seconds() / (24 * 3600) for date in dates]
                if len(sensor_data.items()) > 1: 
                    color = cmap((index / (len(sensor_data.items()) - 1))*0.8+0.1)
                else:
                    color = cmap(0.5)
                plt.plot(days, capacitances, label=sensor_name, color=color, marker='o', markersize=4, linewidth=1.5)
        plt.title(f'Capacitance over Time for {voltage:.2f} V', fontweight='bold', fontsize=16)
        plt.xlabel('Time (Days)', fontweight='bold', fontsize=14)
        plt.ylabel('Capacitance (F)', fontweight='bold', fontsize=14)
        plt.legend(frameon=True, framealpha=0.8, fontsize=12, loc='lower right')
        plt.grid(True, which="both", ls="-", alpha=0.7)
        plt.yscale('log')
        plt.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=6, direction='in')
        plt.tick_params(axis='both', which='minor', width=1, length=4, direction='in')
        plt.minorticks_on()
        y_major = mpl.ticker.LogLocator(base=10, numticks=5)
        y_minor = mpl.ticker.LogLocator(base=10.0, subs=np.arange(1.0, 10.0) * 0.1, numticks=10)
        plt.gca().yaxis.set_major_locator(y_major)
        plt.gca().yaxis.set_minor_locator(y_minor)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'Capacitance_{-voltage:.2f}V.png'))
        plt.close()

    # Plot resistance
    for voltage, sensor_data in voltage_data['resistance'].items():
        plt.style.use('seaborn-whitegrid')
        plt.figure(figsize=(10, 6), dpi=300)
        for index, (sensor_name, measurements) in enumerate(sensor_data.items()):
            if measurements:
                filtered_measurements = filter_outliers(measurements)
                dates, resistances, errors = zip(*filtered_measurements)
                start_date = min(dates)
                days = [(date - start_date).total_seconds() / (24 * 3600) for date in dates]
                if len(sensor_data.items()) > 1: 
                    color = cmap((index / (len(sensor_data.items()) - 1))*0.8+0.1)
                else:
                    color = cmap(0.5)
                plt.errorbar(days, resistances, yerr=errors, fmt='o-', color=color, label=sensor_name, marker='o', markersize=4, linewidth=1.5)
        plt.title(f'Resistance over Time for {voltage:.2f} V', fontweight='bold', fontsize=16)
        plt.xlabel('Time (Days)', fontweight='bold', fontsize=14)
        plt.ylabel('Resistance (Ω)', fontweight='bold', fontsize=14)
        plt.legend(frameon=True, framealpha=0.8, fontsize=12, loc='lower right')
        plt.grid(True, which="both", ls="-", alpha=0.7)
        plt.yscale('log')
        plt.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=6, direction='in')
        plt.tick_params(axis='both', which='minor', width=1, length=4, direction='in')
        plt.minorticks_on()
        y_major = mpl.ticker.LogLocator(base=10, numticks=5)
        y_minor = mpl.ticker.LogLocator(base=10.0, subs=np.arange(1.0, 10.0) * 0.1, numticks=10)
        plt.gca().yaxis.set_major_locator(y_major)
        plt.gca().yaxis.set_minor_locator(y_minor)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'Resistance_{-voltage:.2f}V.png'), bbox_inches='tight')
        plt.close()


def main():
    data_dir = 'data/'
    output_dir = 'output/voltages/'
    
    voltage_data = analyze_sensor_data(data_dir)
    plot_voltage_data(voltage_data, output_dir)

if __name__ == "__main__":
    main()