import time


def generalWarnings(port):
    port.readlines()
    port.write('SR:12\r'.encode())
    time.sleep(1)
    answerGW = port.readline(12)
    answerGW = answerGW[1:(len(answerGW)-1)]
    answerGW = int(answerGW)
    
    if answerGW ==33 :
        print('COOLING SYSTEM FAILED !')
    elif answerGW ==37 :
        print('ABSOLUTE UNDERVOLTAGE MONITORING !') 
    elif answerGW ==38 :
        print('ABSOLUTE OVERVOLTAGE MONITORING !') 
    elif answerGW == 39:
        print('ABSOLUTE UNDERCURRENT MONITORING !') 
    elif answerGW == 43:
        print('EXTERN STOP !') 
    elif answerGW == 46:
        print('EMERGENCY STOP !') 
    elif answerGW == 49:
        print('PRESELECTION EXCEEDING RATED POWER !') 
    elif answerGW == 50:
        print('TUBE OVERPOWER !') 
    elif answerGW == 51:
        print('PRESELECTION OUT OF RANGE !') 
    elif answerGW == 52:
        print('PRESEL. EXCEEDING RATED GENERATOR CURRENT !') 
    elif answerGW == 53:
        print('HIGH VOLTAGE LAMP DEFECTIVE !') 
    elif answerGW == 55:
        print('RELATIVE OVERCURRENT MONITORING !') 
    elif answerGW == 56:
        print('RELATIVE UNDERVOLTAGE MONITORING !') 
    elif answerGW == 60:
        print('RELATIVE UNDERCURRENT MONITORING !') 
    elif answerGW == 63:
        print('DOOR CONTACT 1 AND 2 OPEN !') 
    elif answerGW == 64:
        print('DOOR CONTACT 1 OPEN !') 
    elif answerGW == 65:
        print('DOOR CONTACT 2 OPEN !') 
    elif answerGW == 67:
        print('TEMP. SUPERVISION COOLING SYSTEM !') 
    elif answerGW == 70:
        print('TUBE TO BE WARMED UP ?') 
    elif answerGW == 72:
        print('PRESELECTION OUT OF RANGE !') 
    elif answerGW == 76:
        print('------ STAND BY ------') 
    elif answerGW == 80:
        print('TEMPERATURE SUPERVISION POWER MODULE') 
    elif answerGW == 86:
        print('HV CONTACT FAULTY !') 
    elif answerGW == 90:
        print('FAULT IN FILAMENT CIRCUIT !') 
    elif answerGW == 91:
        print('BUFFER BATTERY EMPTY !') 
    elif answerGW == 96:
        print('SHUTTER NON-SYSTEMATICALLY CLOSED !') 
    elif answerGW == 97:
        print('SHUTTER NOT CONNECTED !') 
    elif answerGW == 98:
        print('SHUTTER NOT OPENED !') 
    elif answerGW == 99:
        print('SHUTTER NOT CLOSED !') 
    elif answerGW == 104:
        print('EXTERNAL WARMPING LAMP FAILED !') 
    elif answerGW == 105:
        print('TEMPERATURE SUPERVISION GENERATOR !') 
    elif answerGW == 106:
        print('WARM UP NECESSARY !') 
    elif answerGW == 108:
        print('POWER FAIL (LOW VOLTAGE) !') 
    elif answerGW == 109:
        print('WARM UP! 0=NO') 
    elif answerGW == 112:
        print('SHUTTER SAFETY CIRCUIT OPEN !') 
    elif answerGW == 113:
        print('ABSOLUTE OVERCURRENT MONITORING !') 
    elif answerGW == 114:
        print('RELATIVE OVERVOLTAGE MONITORING !') 
    elif answerGW == 116:
        print('WARM UP TERMINATED AFTER 3 ATTEMPTS !')
    elif answerGW == 117:
        print('WARM UP ABORTED. TRY AGAIN')
    elif answerGW == 118:
        print('PUSH START BUTTON !')
    else:
        print('ALL OKAY!')

##import serial
##
##
##port = serial.Serial('COM5',timeout=1)
##
##while (True):
##
##    generalWarnings()
##    time.sleep(2)
    
