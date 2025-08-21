import datetime, time
import sys
import re
import yaml

import devices

from xraymachine import XrayMachine

n_shutter = 3 # 3 for obelix


#TODO: remove this function and do the calculation in place
def convertkGyToTime(nkGy, dose_rate=None):
    nSeconds = int(3600.0 / dose_rate * nkGy)
    print(f"calculated number of secconds: {nSeconds}")
    return nSeconds

#TODO : remove magic number
def getCalibratedVoltage(target):
    ## y = k*x +d 
    ## with k = 0.9853
    ##      d = 0
    setpoint = (target ) / 0.9896
    print('setting the voltage to {a:.3f}'.format(a=setpoint))
    return setpoint
    

def biasMOS2000_ON(channel=3):
    print('OBELIX: now turning the MOS2000 bias ON...')
    switch.open_all()
    switch.close_channel(channel)
    sourcemeter_1.set_output_on()
    sourcemeter_1.ramp_voltage(getCalibratedVoltage(10))
    #sourcemeter_1.ramp_voltage(7.)
    time.sleep(2)

def biasMOS2000_OFF(channel=3):
    print('OBELIX: now turning the MOS2000 bias OFF...')
    sourcemeter_1.ramp_voltage(0)
    time.sleep(2)
    switch.open_all()
    sourcemeter_1.set_output_off()
    sourcemeter_1.reset()

#TODO: use datetime for conversions and report in ISO standard
def secondsToHoursMinutesAndSeconds(seconds):
    # return integer hours, minutes, seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    return [hours, minutes, seconds]

def compute_accumulated_dose(remaining_seconds, total_seconds, current_dose_kGy, dose_rate_kGy_per_hr):
    """
    remaining_seconds: seconds left on timer
    total_seconds: total irradiation seconds planned
    current_dose_kGy: starting dose before this irradiation
    dose_rate_kGy_per_hr: kGy per hour
    returns (accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds)
    """
    elapsed = max(0, int(total_seconds - remaining_seconds))
    dose_delivered = (elapsed * float(dose_rate_kGy_per_hr)) / 3600.0
    accumulated = float(current_dose_kGy) + dose_delivered
    return accumulated, dose_delivered, elapsed

def kill_XRM():
    print('OBELIX: SOMEBODY WANTS TO KILL ME!!!')
    print('OBELIX: KILLING IT ALLLLLLLL')
    print('OBELIX: shutdown triggered')
    XRM.closeShutter(n_shutter)    # close obelix shutter
    XRM.hvEnable(False)    # ensure power is off
    time.sleep(1)
    remains = XRM.port.read_all()
    print(f"OBELIX: remains on xrm port comms: {remains}")
    XRM.disconnect()

def get_timer(tn = None):
    try:
        time_left = XRM.getTimer(tn=tn)
    except:
        print("Timer exception")
        time_left = -1      # this is caught by the main irradiation loop as a valueerror

    return time_left

if __name__ == '__main__':

    XRM  = XrayMachine('COM3')

    args = sys.argv

    if args[-1] == 'killObelix':
        kill_XRM()
        exit(0)
    else:
        config_path = args[1]
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

    current_dose = float(args[2])
    target_dose  = float(args[3])
    if current_dose == target_dose:
        print("CURRENT DOSE == TARGET DOSE, NO WORK TO DO, EXITING")   
        XRM.hvEnable(False)    # ensure power is off
        XRM.closeShutter(config['irradiation']['shutter_id'])
        XRM.disconnect()
        exit(0)

    dose_toirr  = target_dose - current_dose
    print('OBELIX: i will irradiate this sample from {a} to {b} kGy. This will add {c} kGy to the total dose!'.format(a=current_dose, b=target_dose, c=dose_toirr))
    time.sleep(2)
    
    if config['irradiation']['biasing'] :
        switch = getattr(devices, config['devices']['switch']['model'])(config['devices']['switch']['address'])
        switch.reset(1)
        switch.get_idn()
        switch.open_all()

        sourcemeter_1 = getattr(devices, config['devices']['sourcemeter_1']['model'])(config['devices']['sourcemeter_1']['address'])
        sourcemeter_1.reset()
        sourcemeter_1.set_source('voltage')
        sourcemeter_1.set_sense('current')
        sourcemeter_1.set_current_limit(config['devices']['sourcemeter_1']['lim_cur'])
        sourcemeter_1.set_voltage(0)
        sourcemeter_1.set_terminal('rear')

    XRM.timerOn(tn=3)          # ensure timer is on
    XRM.hvEnable(False)    # ensure power is off
    
    try:
        # ------- enabling tube, setting up the timer and opening up the shutter -------- 

        XRM.setHighVoltage(config['irradiation']['voltage']) 
        XRM.setCurrent(config['irradiation']['current']) 

        irradiation_seconds = convertkGyToTime(dose_toirr, dose_rate=config['irradiation']['dose_rate'])
        if config['irradiation']['biasing'] :
            biasMOS2000_ON(channel=config['devices']['switch']['connections']['biasMOS2000'])

        XRM.hvEnable(True)
        XRM.waitForWarmUp()
        XRM.setTimer(time = irradiation_seconds, tn = 3)
        XRM.openShutter(config['irradiation']['shutter_id'])

        remaining_time = get_timer(tn = 3)

        # -------- irradiation loop - prints accumulated dose and monitors current and voltage levels ---------
        while(remaining_time > 0):
            remaining_time = get_timer(tn = 3)

            if remaining_time == -1:
                raise ValueError(f"XRM timer returned unexpected value, exiting.")

            TOLERANCE_PERCENT = 5.0
            voltage_deviation = config['irradiation']['voltage'] * (TOLERANCE_PERCENT / 100.0)
            current_deviation = config['irradiation']['current'] * (TOLERANCE_PERCENT / 100.0)
            measured_voltage = XRM.getHighVoltage()
            measured_current = XRM.getCurrent()

            if abs(measured_voltage - config['irradiation']['voltage']) > voltage_deviation:
                raise ValueError(f"Voltage out of tolerance! Set: {config['irradiation']['voltage']} kV, Actual: {measured_voltage} kV")

            if abs(measured_current - config['irradiation']['current']) > current_deviation:
                raise ValueError(f"Current out of tolerance! Set: {config['irradiation']['current']} mA, Actual: {measured_current} mA")
            
            # compute accumulated dose
            accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(remaining_time, irradiation_seconds, current_dose, config['irradiation']['dose_rate'])
            hours_r, minutes_r, seconds_r = secondsToHoursMinutesAndSeconds(remaining_time)
            hours_t, minutes_t, seconds_t = secondsToHoursMinutesAndSeconds(irradiation_seconds)

            sys.stdout.write("\033[F\033[K" * 3)  # move cursor up 3 lines & clear them
            # print progress and accumulated dose
            print(f"OBELIX: Irradiating for in total: {hours_t}:{minutes_t}:{seconds_t}, with  {hours_r}:{minutes_r}:{seconds_r} left")
            print('OBELIX: Dose delivered in this run: {:.6f} kGy (elapsed {:+d} s)'.format(dose_delivered_kGy, elapsed_seconds))
            print('OBELIX: Total accumulated dose so far: {:.6f} kGy'.format(accumulated_total_kGy))

        # ------------------ Finished irradiation -------------------

        accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(remaining_time, irradiation_seconds, current_dose, config['irradiation']['dose_rate'])
        print('OBELIX: irradiation finished normally.')
        print('OBELIX: Total dose delivered this run: {:.6f} kGy'.format(dose_delivered_kGy))
        print('OBELIX: Total accumulated dose = {:.6f} kGy'.format(accumulated_total_kGy))

        kill_XRM()
        if config['irradiation']['biasing'] : biasMOS2000_OFF(channel=config['devices']['switch']['connections']['biasMOS2000'])
        exit(0)
    

    except KeyboardInterrupt: # KI is a BaseException and should be parsed separately 
        print("\nOBELIX: KeyboardInterrupt received — initiating shutdown...")
        kill_XRM()
        if config['irradiation']['biasing']:  biasMOS2000_OFF(channel=config['devices']['switch']['connections']['biasMOS2000'])
        sys.exit(1) #ensures runner termination together with obelix

    except Exception as e:
        print(f"OBELIX: EXCEPTION DURING IRRADIATION: {e}")
        kill_XRM()
        if config['irradiation']['biasing']: biasMOS2000_OFF(channel=config['devices']['switch']['connections']['biasMOS2000'])
        print('OBELIX: irradiation stopped unexpectedly.')
        sys.exit(1) #ensures runner termination together with obelix
