import serial
import datetime, time
import sys
import os
from time import gmtime, strftime
import re
from obelixWarnings import generalWarnings


def convertkGyToTime(nkGy):
    ## the dose rate anne is 24.26389 kGy per hour
    ## that means anne kGy per 3600 seconds
    ## that in turn means 3600/anne = 148.36862514625642 seconds per kGy

    ## doseRate = 24.26389 ## this is at 19.6 cm
    #doseRate = 13.2465  ## this is at 24.6 cm
    ## used for N4789-12_UL doseRate = 39.1895  ## value taken on november 1st 2021
    doseRate = 14.257  ## value taken on Aug 31st 2023
    doseRate = doseRate ##
    nSeconds = int(3600./doseRate * nkGy)
    hms = str(datetime.timedelta(seconds=nSeconds))
    hms = [int(i) for i in hms.split(':')]
    return hms[0], hms[1], hms[2]

# def getCalibratedVoltage(target):
#     ## y = k*x +d 
#     ## with k = 0.9853
#     ##      d = 0
#     setpoint = (target ) / 0.9896
#     print('setting the voltage to {a:.3f}'.format(a=setpoint))
#     return setpoint
    

def convertToBinary(word):
    word = word[1:];
    word = word[:len(word)-1];
    binary= bin(int(word));
    binary = binary[2:].zfill(8);            #delete 0b at the beginning of the binarySR4 string and fill with zeros
    return binary


def statusRead4():    #status window 3 and 4
    string = 'SR:04\r';    
    port.readlines()
    port.write( string.encode() );
    #answerSR4 = "*0000000064";
    answerSR4 = port.readline(12);
    binarySR4 = convertToBinary(answerSR4)
    #answerSR4 = answerSR4[1:];
    #answerSR4 = answerSR4[:len(answerSR4)-1];
    #binarySR4 = bin(int(answerSR4));
    #binarySR4 = binarySR4[2:].zfill(8);            #delete 0b at the beginning of the binarySR4 string and fill with zeros
    port.readlines()
    port.write('SR:01\r'.encode())
    answerSR1 = port.readline(12)
    binarySR1 = convertToBinary(answerSR1)
    port.readlines()
    port.write('SR:02\r'.encode())
    answerSR2 = port.readline(12)
    binarySR2 = convertToBinary(answerSR2)
    ##  binarySR4[0]         shutter command OPEN for shutter 3
    ##  binarySR4[1]         shutter status shutter 3 OPEN
    ##  binarySR2[2]         timer 3 ON
    ##  binarySR1[1]         high voltage ON
    ##  (binarySR1[2] == 0)  cooling circuit OK
    ##  (binarySR1[4] == 0)  actualCurrent == nominalCurrent
    ##  (binarySR1[5] == 0)  actualVoltage == nominalVoltage
    if (   not int(binarySR4[0]) \
        or not int(binarySR4[1]) \
        or not int(binarySR2[2]) \
        or not int(binarySR1[1]) \
        or     int(binarySR1[2])  \
        or     int(binarySR1[4])  \
        or     int(binarySR1[5]) ) :
        print ("OBELIX: Unexpected status word (concerning shutter 3)")
        if (int(binarySR4[0]) == 0): print('OBELIX ERROR: shutter command CLOSED for shutter 3')
        if (int(binarySR4[1]) == 0): print('OBELIX ERROR: shutter status shutter 3 CLOSED')
        if (int(binarySR2[2]) == 0): print('OBELIX ERROR: timer 3 OFF')
        if (int(binarySR1[1]) == 0): print('OBELIX ERROR: high voltage OFF')
        if (int(binarySR1[2]) == 1): print('OBELIX ERROR: cooling circuit NOT OK')
        if (int(binarySR1[4]) == 1): print('OBELIX ERROR: actualCurrent NOT EQUAL to nominalCurrent')
        if (int(binarySR1[5]) == 1): print('OBELIX ERROR: actualVoltage NOT EQUAL to nominalVoltage')
        print ("OBELIX: Program will now end")
        print ("OBELIX: Closing shutter 3 and turning off the HV!")
        port.write('CS:3\r'.encode())
        port.write('HV:0\r'.encode())
        #check
        if (readExposureTimerActualValue(3) != 0):
            exit(1)
    else:
        print ("OBELIX: all irradiation parameters look okay")
        return 1


def testCurrent(int_current_mA):
    if(int_current_mA < 2 or int_current_mA > 80 or type(int_current_mA) != int):
        return False;    
    return True;

def nominalCurrent():
    port.readlines()
    string = 'CN\r';
    port.write(string.encode());#request nominal current
    #answerCN = "*0000032000";
    answerCN = port.readline(12);
    answerCN = int(answerCN[1:]);#Delete*in the front of the answer
    return int(answerCN/1000);


def actualCurrent():
    port.readlines()
    port.write( 'CA\r'.encode() );    #Request actual current
    #answerCA = "*0000032000";
    answerCA = port.readline(12);
    answerCA = int(answerCA[1:]);
    return int(answerCA/1000);


def setCurrent(int_current_mA):
    if(testCurrent(int_current_mA) == False):
        exit(1)
    string = 'SC:%02d\r' % int_current_mA;    #Produce right formatted command (carriage return at the end)
    port.readlines()
    port.write( string.encode() );    #Write string to port
    time.sleep(3);                     #Wait three seconds before sending new request
    counter = 1;
    while(True):
        answerCN = nominalCurrent();
        if(float(int_current_mA) == float(answerCN)):
            break;
        if(counter == 3):#After 3 unsuccesful requests the function will end 
            return False;
        counter = counter + 1;
        time.sleep(3);
    counter = 1;
    ##while(True):
    ##    answerCA = actualCurrent();
    ##    if(float(int_current_mA) == float(answerCA)):
    ##        break;
    ##    if(counter == 5):            #After 5 unsuccesful requests the function will end 
    ##        print ("Can't receive actual current (after 5 tries)\n");
    ##        return False;
    ##    counter = counter + 1;
    ##    time.sleep(3);
    print (">> Actual current has reached {0}mA".format(int_current_mA));
    return answerCN;



def testVoltage(int_voltage_kV):
    if(int_voltage_kV < 2 or int_voltage_kV > 60 or type(int_voltage_kV) != int):
        return False;
    return True;


def nominalVoltage():
    port.readlines()
    port.write( 'VN\r'.encode() );    #Request nominal current
    #answerVN = "*0000032000";
    answerVN = port.readline(12);
    answerVN = int(answerVN[1:]);    #Delete * in the front of the answer
    return int(answerVN/1000);


def actualVoltage():
    port.readlines()
    port.write( 'VA\r'.encode() );    #Request actual current
    #answerVA = "*0000032000";
    #print('this is readlines', port.readlines())
    answerVA = port.readline(12);
    answerVA = int(answerVA[1:]);    #Delete * in the front of the answer
    return int(answerVA/1000);

def setVoltage(int_voltage_kV):
    if(testVoltage(int_voltage_kV) == False):
        print ("Please type a integer variable between 2 and 60 kV for the voltage\n");
        exit(1)
    #print string;
    port.readlines()
    string = 'SV:%02d\r' % int_voltage_kV;    #Produce right formatted command
    port.write( string.encode() );    #Write string to port
    port.readlines()
    counter = 1;
    while(True):
        answerVN = nominalVoltage();
        if(float(int_voltage_kV) == float(answerVN)):
            break;
        if(counter == 3):            #After 3 unsuccesful requests the function will end 
            print ("Could not set or receive the nominal voltage\n");
            exit(1)
        counter = counter + 1;
    counter = 1;
    ##while(True):
    ##    answerVA = actualVoltage();
    ##    if(float(1000*int_voltage_kV) == float(answerVA)):
    ##        break;
    ##    if(counter == 5):            #After 5 unsuccesful requests the function will end 
    ##        print ("Could not receive the actual voltage\n");
    ##        sys.exit();
    ##        #return False;
    ##    counter = counter + 1;
    ##print (">> Actual voltage has reached {0}kV.").format(int_voltage_kV);
    return answerVN;

def turnHVOn():
    port.readlines()
    print('OBELIX: now turning on the HV')
    port.write('HV:1\r'.encode())
    port.readlines()
    
    nom_volt, nom_curr = nominalVoltage(), nominalCurrent()
    act_volt, act_curr = actualVoltage(), actualCurrent()

    print('OBELIX: nominal voltage and current are:', nom_volt, nom_curr)
    print('OBELIX: now making sure that they correspond to the actual values')

    while(nom_volt != act_volt):
        act_volt = actualVoltage()
        print('OBELIX: set and actual voltage', nom_volt, act_volt)

    while(nom_curr != act_curr):
        act_curr = actualCurrent()
        print('OBELIX: set and actual currage', nom_curr, act_curr)

    print('OBELIX: the actual voltage is', act_volt)
    print('OBELIX: the actual current is', act_curr)
    

def openShutter(int_shutternumber, override=''):
    if not override:
        a = input('ATTENTION: are you sure you want to start irradiation (type "yes" if so)? ')
        if not a in ['y', 'yes', 'YES', 'Y']:
            port.write('HV:0\r'.encode())
            exit(1)

    elif override in ['y', 'yes', 'YES', 'Y']:
        print('OBELIX: overriding manual user input. will try to open shutter NOW!')
        time.sleep(3)

    else:
        port.write('HV:0\r'.encode())
        exit(1)
    
    while(int_shutternumber != 2 and int_shutternumber != 3 or type(int_shutternumber) != int):
        int_shutternumber = input("OBELIX: Please choose a correct shutternumber to open (2 (back) or 3 (down)... ");

    port.readlines()
    port.write('CC:0010\r'.encode())
    port.readlines()

    string = 'OS:%01d\r' % int_shutternumber;    #Produce right formatted command
    port.write( string.encode() );
    time.sleep(1)
    if(int_shutternumber == 3):
        return statusRead4();


def closeShutter(int_shutternumber):
    while(int_shutternumber != 2 and int_shutternumber != 3 or type(int_shutternumber) != int):
        int_shutternumber = input("OBELIX: Please choose a correct shutternumber to close (2 (back) or 3 (down)... ");
    string = 'CS:%01d\r' % int_shutternumber;    #Produce right formatted command
    #print string;
    port.write( string.encode() );
    time.sleep(3);
    if(int_shutternumber == 3):
        return(not statusRead4());


def validateSetTimerString(setTimerString):
    reg = re.match(r'([ ]*)([0-9]{1}) ([0-9]{2}) ([0-9]{2}) ([0-9]{2})([ ]*)',setTimerString)
    #print('reg.group(2): ',reg.group(2),' reg.group(3): ',reg.group(3),' reg.group(4): ',reg.group(4))
    if reg == None:
        print('OBELIX: Please enter the information as: %1 %02 %02 %02');
        return 
    else:
        if not (0<=int(reg.group(3)) and int(reg.group(3)) <= 99):
            print('Enter a valid hour number')
            return 
        elif not (0<=int(reg.group(4)) and int(reg.group(4)) < 60):
            print('Enter a valid minutes number')
            return 
        elif not (0<=int(reg.group(5)) and int(reg.group(5))<60):
            print('Enter a valid seconds number')
            return 
        else:
            print('>> Timer string validated')
            return [int(reg.group(2)), int(reg.group(3)), int(reg.group(4)), int(reg.group(5))]
            




def exposureTimerOn (n):
    port.write('SR:02\n'.encode())
    time.sleep(1)
    #receivedString = port.readline(12)
    receivedString = '*0000000034\r'
    receivedString = receivedString[1:(len(receivedString)-1)]

    if n == 1 and bin(int(receivedString))[2] == 0: 
        port.write(('TS:%1d\r' %n).encode());
        print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
    elif n==2 and bin(int(receivedString))[3] == 0:
        port.write(('TS:%1d\r' %n).encode());
        print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
    elif n==3 and bin(int(receivedString))[4] == 0:
        port.write(('TS:%1d\r' %n).encode());
        print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
    elif n==4 and bin(int(receivedString))[5] == 0:
        port.write(('TS:%1d\r' %n).encode());
        print('>> Exposure Timer is ON: (TS:%1d)\r' %n)
    else:
        return True
    return False



def nominalExposureTimer(n):
    port.write(('TN:%1d\r' %n).encode())
    time.sleep(1)
    answerNET = port.readline(12)
    return answerNET[1:]


def actualExposureTimer(n):
    port.write(('TA:%1d\r' %n).encode())
    time.sleep(1)
    answerAET = port.readline(12)
    return answerAET[1:]


## timer number 3!
def setExposureTimer(n,hours,minutes,seconds):

    print('OBELIX: setting the exposure timer to {h} hours, {m} minutes, and {s} seconds'.format(h=hours,m=minutes,s=seconds))
    #if not exposureTimerOn(n):
    string = 'TP:%1d,%02d,%02d,%02d\r' % (n,hours,minutes,seconds);
    
    port.write(string.encode());
    time.sleep(1)
    port.write(('TN:%1d\r' %n).encode())
    time.sleep(1)
    print('making sure that the timer is on!')
    port.write(('TS:%1d\r' %n).encode())
    time.sleep(1)
    
    exposureTimerSetpointValue = (hours*3600 + minutes*60 + seconds)
    counter = 1
    while(True):
        answerNET = nominalExposureTimer(n)
        if exposureTimerSetpointValue == int(answerNET):
            break;
        if counter == 5:
            print('Could not set or receive the nominal timer \n')
            exit(5)
        counter+=1
    counter = 1
    while(True):
        answerAET = actualExposureTimer(n)
        if exposureTimerSetpointValue == int(answerAET):
            break;
        if counter == 5:
            print('Could not set or receive the actual timer \n')
            exit(6)
        counter+=1
        
    print('>> Exposure Timer is Set: ('+string[:len(string)-1]+')\r')
    return
    #else:
    #    print("This timer is already On")


def secondsToHoursMinutesAndSeconds(seconds):
    
    hours = int(seconds/3600)
    minutes = int((seconds % 3600)/60)
    seconds = ((seconds % 3600) % 60)

    return [hours, minutes, seconds]


def readExposureTimerActualValue(n):

    port.readlines()
    port.write(('TA:%1d\r' %n).encode())
    #time.sleep(1)
    exposureTimerSeconds = port.readline(12)
    exposureTimerSeconds = exposureTimerSeconds[1:(len(exposureTimerSeconds)-1)]
    return int(exposureTimerSeconds)
    


if __name__ == '__main__':

    #From now on it's the main code
    
    port = serial.Serial('COM3',baudrate = 9600,timeout=1)

    args = sys.argv

    if args[-1] == 'killObelix':
        if statusRead4():
            print('OBELIX: SOMEBODY WANTS TO KILL ME!!!')
            print('OBELIX: KILLING IT ALLLLLLLL')
            port.write('CS:3\r'.encode())
            port.write('HV:0\r'.encode())
            print('exiting after keyboard interrupt')
            exit(0)

    _currentDose = float(args[1])
    _targetDose  = float(args[2])

        

    _overrideUserInput = ''
    if len(args) > 3:
        _overrideUserInput = args[3]
    
    
    try:
        #inputVoltage = input("Enter the voltage of the tube in kV ") 
        nom_volt = setVoltage(40) #int(inputVoltage))
        #inputCurrent = input("Enter the current of the tube in mA ")
        nom_curr = setCurrent(50) #int(inputCurrent))
        validateSetTimerStringRet = None
        ##while(validateSetTimerStringRet == None):
        ##    setTimerString = input("Enter the exposure timer number, the hours, minutes and seconds (use spaces between values) ")
        ##    validateSetTimerStringRet = validateSetTimerString(setTimerString)

        dose_current = _currentDose #float(input('OBELIX: enter the CURRENT dose of the sample'))
        dose_target  = _targetDose  #float(input('OBELIX: enter the TARGET  dose of the sample'))
        dose_toirr  = dose_target - dose_current
  
        print('OBELIX: i will irradiate this sample from {a} to {b} kGy. This will add {c} kGy to the total dose!'.format(a=dose_current, b=dose_target, c=dose_toirr))
        hours, minutes, seconds = convertkGyToTime(dose_toirr)
        setExposureTimer(3, hours, minutes, seconds)
        #remainingTimeInSeconds = (int(validateSetTimerStringRet[1]) * 3600 + int(validateSetTimerStringRet[2]) * 60 + int(validateSetTimerStringRet[3]))
        #shutterNumber = input("Enter the shutter number ")
        remainingTimeInSeconds = readExposureTimerActualValue(3)
        turnHVOn()
        openShutter(3, _overrideUserInput) #int(shutterNumber))
        while(remainingTimeInSeconds):
            remainingTimeInSeconds = readExposureTimerActualValue(3)
            hours, minutes, seconds = secondsToHoursMinutesAndSeconds(remainingTimeInSeconds)
            #print('>> Elapsed Time in Seconds: %d' %elapsedTimeInSeconds)
            print('OBELIX: i am currently irradiating from {a} to {b} kGy; total time: {h}h {m}m {s}s'.format(a=dose_current,b=dose_target,h=hours,m=minutes,s=seconds))
            print('>> Still irradiating for: %02d Hours %02d Minutes and %02d Seconds' %(hours,minutes,seconds))
            generalWarnings(port)
            ret = statusRead4()
            if ret == -1:
                pass
            time.sleep(1)
    
    except: #Exception as e:
        print('OBELIX: EXCEPTION RAISED!!!')
        port.write('CS:3\r'.encode())
        port.write('HV:0\r'.encode())
        print('exiting after keyboard interrupt')
        exit(1)
    
