import serial
import datetime, time
import sys
import re
import yaml

from obelixWarnings import generalWarnings

import devices

from xraymachine import XrayMachine

n_shutter = 3 # 3 for obelix


def convertkGyToTime(nkGy, dose_rate=None):
    nSeconds = int(3600.0 / dose_rate * nkGy)
    print(f"calculated number of secconds: {nSeconds}")
    # hms = str(datetime.timedelta(seconds=nSeconds))
    # hms = [int(i) for i in hms.split(':')]
    return nSeconds

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

# def convertToBinary(word):
#     word = word[1:];
#     word = word[:len(word)-1];
#     binary= bin(int(word));
#     binary = binary[2:].zfill(8);            #delete 0b at the beginning of the binarySR4 string and fill with zeros
#     return binary


# def statusRead4():    #status window 3 and 4
#     string = 'SR:04\r';    
#     port.readlines()
#     port.write( string.encode() );
#     #answerSR4 = "*0000000064";
#     answerSR4 = port.readline(12);
#     binarySR4 = convertToBinary(answerSR4)
#     #answerSR4 = answerSR4[1:];
#     #answerSR4 = answerSR4[:len(answerSR4)-1];
#     #binarySR4 = bin(int(answerSR4));
#     #binarySR4 = binarySR4[2:].zfill(8);            #delete 0b at the beginning of the binarySR4 string and fill with zeros
#     port.readlines()
#     port.write('SR:01\r'.encode())
#     answerSR1 = port.readline(12)
#     binarySR1 = convertToBinary(answerSR1)
#     port.readlines()
#     port.write('SR:02\r'.encode())
#     answerSR2 = port.readline(12)
#     binarySR2 = convertToBinary(answerSR2)
#     ##  binarySR4[0]         shutter command OPEN for shutter 3
#     ##  binarySR4[1]         shutter status shutter 3 OPEN
#     ##  binarySR2[2]         timer 3 ON
#     ##  binarySR1[1]         high voltage ON
#     ##  (binarySR1[2] == 0)  cooling circuit OK
#     ##  (binarySR1[4] == 0)  actualCurrent == nominalCurrent
#     ##  (binarySR1[5] == 0)  actualVoltage == nominalVoltage
#     if (   not int(binarySR4[0]) \
#         or not int(binarySR4[1]) \
#         or not int(binarySR2[2]) \
#         or not int(binarySR1[1]) \
#         or     int(binarySR1[2])  \
#         or     int(binarySR1[4])  \
#         or     int(binarySR1[5]) ) :
#         print ("OBELIX: Unexpected status word (concerning shutter 3)")
#         if (int(binarySR4[0]) == 0): print('OBELIX ERROR: shutter command CLOSED for shutter 3')
#         if (int(binarySR4[1]) == 0): print('OBELIX ERROR: shutter status shutter 3 CLOSED')
#         if (int(binarySR2[2]) == 0): print('OBELIX ERROR: timer 3 OFF')
#         if (int(binarySR1[1]) == 0): print('OBELIX ERROR: high voltage OFF')
#         if (int(binarySR1[2]) == 1): print('OBELIX ERROR: cooling circuit NOT OK')
#         if (int(binarySR1[4]) == 1): print('OBELIX ERROR: actualCurrent NOT EQUAL to nominalCurrent')
#         if (int(binarySR1[5]) == 1): print('OBELIX ERROR: actualVoltage NOT EQUAL to nominalVoltage')
#         print ("OBELIX: Program will now end")
#         print ("OBELIX: Closing shutter 3 and turning off the HV!")
#         port.write('CS:3\r'.encode())
#         port.write('HV:0\r'.encode())
#         biasMOS2000_OFF(channel=3)
#         #check
#         if (readExposureTimerActualValue(3) != 0):
#             exit(1)
#     else:
#         print ("OBELIX: all irradiation parameters look okay")
#         return 1

# def testCurrent(int_current_mA):
#     if(int_current_mA < 2 or int_current_mA > 80 or type(int_current_mA) != int):
#         return False;    
#     return True;

# def nominalCurrent():
#     port.readlines()
#     string = 'CN\r';
#     port.write(string.encode());#request nominal current
#     #answerCN = "*0000032000";
#     answerCN = port.readline(12);
#     answerCN = int(answerCN[1:]);#Delete*in the front of the answer
#     return int(answerCN/1000);

# def actualCurrent():
#     port.readlines()
#     port.write( 'CA\r'.encode() );    #Request actual current
#     #answerCA = "*0000032000";
#     answerCA = port.readline(12);
#     answerCA = int(answerCA[1:]);
#     return int(answerCA/1000);

# def setCurrent(int_current_mA):
#     if(testCurrent(int_current_mA) == False):
#         exit(1)
#     string = 'SC:%02d\r' % int_current_mA;    #Produce right formatted command (carriage return at the end)
#     port.readlines()
#     port.write( string.encode() );    #Write string to port
#     time.sleep(3);                     #Wait three seconds before sending new request
#     counter = 1;
#     while(True):
#         answerCN = nominalCurrent();
#         if(float(int_current_mA) == float(answerCN)):
#             break;
#         if(counter == 3):#After 3 unsuccesful requests the function will end 
#             return False;
#         counter = counter + 1;
#         time.sleep(3);
#     counter = 1;
#     ##while(True):
#     ##    answerCA = actualCurrent();
#     ##    if(float(int_current_mA) == float(answerCA)):
#     ##        break;
#     ##    if(counter == 5):            #After 5 unsuccesful requests the function will end 
#     ##        print ("Can't receive actual current (after 5 tries)\n");
#     ##        return False;
#     ##    counter = counter + 1;
#     ##    time.sleep(3);
#     print (">> Actual current has reached {0}mA".format(int_current_mA));
#     return answerCN;

# def testVoltage(int_voltage_kV):
#     if(int_voltage_kV < 2 or int_voltage_kV > 60 or type(int_voltage_kV) != int):
#         return False;
#     return True;

# def nominalVoltage():
#     port.readlines()
#     port.write( 'VN\r'.encode() );    #Request nominal current
#     #answerVN = "*0000032000";
#     answerVN = port.readline(12);
#     answerVN = int(answerVN[1:]);    #Delete * in the front of the answer
#     return int(answerVN/1000);

# def actualVoltage():
#     port.readlines()
#     port.write( 'VA\r'.encode() );    #Request actual current
#     #answerVA = "*0000032000";
#     #print('this is readlines', port.readlines())
#     answerVA = port.readline(12);
#     answerVA = int(answerVA[1:]);    #Delete * in the front of the answer
#     return int(answerVA/1000);

# def setVoltage(int_voltage_kV):
#     if(testVoltage(int_voltage_kV) == False):
#         print ("Please type a integer variable between 2 and 60 kV for the voltage\n");
#         exit(1)
#     #print string;
#     port.readlines()
#     string = 'SV:%02d\r' % int_voltage_kV;    #Produce right formatted command
#     port.write( string.encode() );    #Write string to port
#     port.readlines()
#     counter = 1;
#     while(True):
#         answerVN = nominalVoltage();
#         if(float(int_voltage_kV) == float(answerVN)):
#             break;
#         if(counter == 3):            #After 3 unsuccesful requests the function will end 
#             print ("Could not set or receive the nominal voltage\n");
#             exit(1)
#         counter = counter + 1;
#     counter = 1;
#     ##while(True):
#     ##    answerVA = actualVoltage();
#     ##    if(float(1000*int_voltage_kV) == float(answerVA)):
#     ##        break;
#     ##    if(counter == 5):            #After 5 unsuccesful requests the function will end 
#     ##        print ("Could not receive the actual voltage\n");
#     ##        sys.exit();
#     ##        #return False;
#     ##    counter = counter + 1;
#     ##print (">> Actual voltage has reached {0}kV.").format(int_voltage_kV);
#     return answerVN;

# def turnHVOn():
#     port.readlines()
#     print('OBELIX: now turning on the HV')
#     port.write('HV:1\r'.encode())
#     port.readlines()
    
#     nom_volt, nom_curr = nominalVoltage(), nominalCurrent()
#     act_volt, act_curr = actualVoltage(), actualCurrent()

#     print('OBELIX: nominal voltage and current are:', nom_volt, nom_curr)
#     print('OBELIX: now making sure that they correspond to the actual values')

#     while(nom_volt != act_volt):
#         act_volt = actualVoltage()
#         print('OBELIX: set and actual voltage', nom_volt, act_volt)

#     while(nom_curr != act_curr):
#         act_curr = actualCurrent()
#         print('OBELIX: set and actual currage', nom_curr, act_curr)

#     print('OBELIX: the actual voltage is', act_volt)
#     print('OBELIX: the actual current is', act_curr)
    
# def openShutter(int_shutternumber, override=''):
#     if not override:
#         a = input('ATTENTION: are you sure you want to start irradiation (type "yes" if so)? ')
#         if not a in ['y', 'yes', 'YES', 'Y']:
#             port.write('HV:0\r'.encode())
#             biasMOS2000_OFF(channel=3)
#             exit(1)

#     elif override in ['y', 'yes', 'YES', 'Y']:
#         print('OBELIX: overriding manual user input. will try to open shutter NOW!')
#         time.sleep(3)

#     else:
#         port.write('HV:0\r'.encode())
#         biasMOS2000_OFF(channel=3)
#         exit(1)
    
#     while(int_shutternumber != 2 and int_shutternumber != 3 or type(int_shutternumber) != int):
#         int_shutternumber = input("OBELIX: Please choose a correct shutternumber to open (2 (back) or 3 (down)... ");

#     port.readlines()
#     port.write('CC:0010\r'.encode())
#     port.readlines()

#     string = 'OS:%01d\r' % int_shutternumber;    #Produce right formatted command
#     port.write( string.encode() );
#     time.sleep(1)
#     if(int_shutternumber == 3):
#         return statusRead4();

# def closeShutter(int_shutternumber):
#     while(int_shutternumber != 2 and int_shutternumber != 3 or type(int_shutternumber) != int):
#         int_shutternumber = input("OBELIX: Please choose a correct shutternumber to close (2 (back) or 3 (down)... ");
#     string = 'CS:%01d\r' % int_shutternumber;    #Produce right formatted command
#     #print string;
#     port.write( string.encode() );
#     time.sleep(3);
#     if(int_shutternumber == 3):
#         return(not statusRead4());

# def validateSetTimerString(setTimerString):
#     reg = re.match(r'([ ]*)([0-9]{1}) ([0-9]{2}) ([0-9]{2}) ([0-9]{2})([ ]*)',setTimerString)
#     #print('reg.group(2): ',reg.group(2),' reg.group(3): ',reg.group(3),' reg.group(4): ',reg.group(4))
#     if reg == None:
#         print('OBELIX: Please enter the information as: %1 %02 %02 %02');
#         return 
#     else:
#         if not (0<=int(reg.group(3)) and int(reg.group(3)) <= 99):
#             print('Enter a valid hour number')
#             return 
#         elif not (0<=int(reg.group(4)) and int(reg.group(4)) < 60):
#             print('Enter a valid minutes number')
#             return 
#         elif not (0<=int(reg.group(5)) and int(reg.group(5))<60):
#             print('Enter a valid seconds number')
#             return 
#         else:
#             print('>> Timer string validated')
#             return [int(reg.group(2)), int(reg.group(3)), int(reg.group(4)), int(reg.group(5))]

# def exposureTimerOn (n):
#     port.write('SR:02\n'.encode())
#     time.sleep(1)
#     #receivedString = port.readline(12)
#     receivedString = '*0000000034\r'
#     receivedString = receivedString[1:(len(receivedString)-1)]

#     if n == 1 and bin(int(receivedString))[2] == 0: 
#         port.write(('TS:%1d\r' %n).encode());
#         print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
#     elif n==2 and bin(int(receivedString))[3] == 0:
#         port.write(('TS:%1d\r' %n).encode());
#         print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
#     elif n==3 and bin(int(receivedString))[4] == 0:
#         port.write(('TS:%1d\r' %n).encode());
#         print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
#     elif n==4 and bin(int(receivedString))[5] == 0:
#         port.write(('TS:%1d\r' %n).encode());
#         print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
#     else:
#         return True
#     return False

# def nominalExposureTimer(n):
#     port.write(('TN:%1d\r' %n).encode())
#     time.sleep(1)
#     answerNET = port.readline(12)
#     return answerNET[1:]

# def actualExposureTimer(n):
#     port.write(('TA:%1d\r' %n).encode())
#     time.sleep(1)
#     answerAET = port.readline(12)
#     return answerAET[1:]

# def setExposureTimer(n,hours,minutes,seconds):

#     print('OBELIX: setting the exposure timer to {h} hours, {m} minutes, and {s} seconds'.format(h=hours,m=minutes,s=seconds))
#     #if not exposureTimerOn(n):
#     string = 'TP:%1d,%02d,%02d,%02d\r' % (n,hours,minutes,seconds);
    
#     port.write(string.encode());
#     time.sleep(1)
#     port.write(('TN:%1d\r' %n).encode())
#     time.sleep(1)
#     print('making sure that the timer is on!')
#     port.write(('TS:%1d\r' %n).encode())
#     time.sleep(1)
    
#     exposureTimerSetpointValue = (hours*3600 + minutes*60 + seconds)
#     counter = 1
#     while(True):
#         answerNET = nominalExposureTimer(n)
#         if exposureTimerSetpointValue == int(answerNET):
#             break;
#         if counter == 5:
#             print('Could not set or receive the nominal timer \n')
#             exit(5)
#         counter+=1
#     counter = 1
#     while(True):
#         answerAET = actualExposureTimer(n)
#         if exposureTimerSetpointValue == int(answerAET):
#             break;
#         if counter == 5:
#             print('Could not set or receive the actual timer \n')
#             exit(6)
#         counter+=1
        
#     print('>> Exposure Timer is Set: ('+string[:len(string)-1]+')\r')
#     return
#     #else:
#     #    print("This timer is already On")

def secondsToHoursMinutesAndSeconds(seconds):
    # return integer hours, minutes, seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    return [hours, minutes, seconds]

# def readExposureTimerActualValue(n):

#     port.readlines()
#     port.write(('TA:%1d\r' %n).encode())
#     #time.sleep(1)
#     exposureTimerSeconds = port.readline(12)
#     exposureTimerSeconds = exposureTimerSeconds[1:(len(exposureTimerSeconds)-1)]
#     return int(exposureTimerSeconds)

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
    # print('OBELIX: SOMEBODY WANTS TO KILL ME!!!')
    # print('OBELIX: KILLING IT ALLLLLLLL')
    print('OBELIX: shutdown triggered')
    XRM.closeShutter(n_shutter)    # close obelix shutter
    XRM.hvEnable(False)    # ensure power is off
    time.sleep(1)
    remains = XRM.port.read_all
    print(f"remains on xrm port comms: {remains}")
    XRM.disconnect

def get_timer(tn = None):
    try:
        time_left = XRM.getTimer(tn=tn)
    except:
        print("Timer exception")
        time_left = 0

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
            # print("Loaded config:")
            # print(yaml.dump(config, default_flow_style=False))


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
        XRM.setHighVoltage(config['irradiation']['voltage']) 
        XRM.setCurrent(config['irradiation']['current']) 

        # print('OBELIX: i will irradiate this sample from {a} to {b} kGy. This will add {c} kGy to the total dose!'.format(a=current_dose, b=target_dose, c=dose_toirr))
        irradiation_seconds = convertkGyToTime(dose_toirr, dose_rate=config['irradiation']['dose_rate'])

        # total irradiation time in seconds (used to compute elapsed vs remaining)
        # irradiation_seconds = int(hours * 3600 + minutes * 60 + seconds)

        if config['irradiation']['biasing'] :
            biasMOS2000_ON(channel=config['devices']['switch']['connections']['biasMOS2000'])

        XRM.hvEnable(True)
        XRM.waitForWarmUp()
        XRM.setTimer(time = irradiation_seconds, tn = 3)
        XRM.openShutter(config['irradiation']['shutter_id'])

        remaining_time = get_timer(tn = 3)

        # irradiation loop - prints accumulated dose continuously
        while(remaining_time > 0):
            remaining_time = get_timer(tn = 3)
            # ------- check current and voltage values -------- 
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
            print(f"OBELIX: irradiating for in total: {hours_t}:{minutes_t}:{seconds_t}, with  {hours_r}:{minutes_r}:{seconds_r} left")
            print('>> Dose delivered in this run: {:.6f} kGy (elapsed {:+d} s)'.format(dose_delivered_kGy, elapsed_seconds))
            print('>> Total accumulated dose so far: {:.6f} kGy'.format(accumulated_total_kGy))


        # ------------------ Finished irradiation -------------------

        accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(0, irradiation_seconds, current_dose, config['irradiation']['dose_rate'])
        print('OBELIX: irradiation finished normally.')
        print('OBELIX: Total dose delivered this run: {:.6f} kGy'.format(dose_delivered_kGy))
        print('OBELIX: Total accumulated dose = {:.6f} kGy'.format(accumulated_total_kGy))

        kill_XRM()
        if config['irradiation']['biasing'] : biasMOS2000_OFF(channel=config['devices']['switch']['connections']['biasMOS2000'])
        
        exit(0)
    
    except Exception as e:
        # try to recover the accumulated dose if an exception occurred during irradiation. 
        print(f"OBELIX: EXCEPTION DURING IRRADIATION: {e}")
        try:
            accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(get_timer(tn=3), irradiation_seconds, current_dose, config['irradiation']['dose_rate'])
        except Exception as e2:
                print(f"OBELIX: FAILED TO READ TIMER AFTER EXCEPTION DURING IRRADIATION: {e2}")
                print('OBELIX: SHUTTING DOWN')

        kill_XRM()
        if config['irradiation']['biasing'] : biasMOS2000_OFF(channel=config['devices']['switch']['connections']['biasMOS2000'])

        print('OBELIX: irradiation stopped unexpectedly.')

        exit(1)
