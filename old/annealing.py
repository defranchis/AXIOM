import subprocess, signal
import time
from datetime import datetime, timedelta

## change the sensorName before starting anything!
oxidename = "200um" # No spaces here please
sensorName = 'C_200261_200um'

restBetweenMeasurements = 2.5 * 3600        # In seconds
totalTime = (24*30 + 12) * 3600

cmd = 'testMD_fullStrip'

begining = datetime.now()


measurements = subprocess.run(['python', '.\main.py', 'Strip_{n}_m20C_{b}s'.format(n=sensorName, b=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')), cmd], check=True)
lastmeasurementTime = datetime.now()


try:
    while(True):
        if (datetime.now()-lastmeasurementTime).total_seconds() > restBetweenMeasurements:
            try:
                measurements = subprocess.run(['python', '.\main.py', 'Strip_{n}_m20C_{b}s'.format(n=sensorName, b=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')), cmd], check=True)
                #print("Plotting data...")
                #plots = subprocess.run(['python', '.\plotter\main.py', oxidename, sensorName], check=True)
            except Exception as e:
                print("*********ERROR*********")
                print(e)
                print("***********************")
            lastmeasurementTime = datetime.now()
        else:
            print("Waiting for next measurement. Remaining time [s]:", timedelta(seconds=int(restBetweenMeasurements-(datetime.now()-lastmeasurementTime).total_seconds())))
            time.sleep(1)

## if anything exits with anything other than exit(0), 
## we end up in the subprocess exception, and everything stops
except subprocess.CalledProcessError as e:
    print(e) ## print the exception
    #if e == KeyboardInterrupt:
    #obelix       .send_signal(signal.SIGINT)
    #measurements .send_signal(signal.SIGINT)
    ## write an email to matteo

except KeyboardInterrupt:
    obelix = subprocess.run(['python', '.\obelixControl_Strip.py', 'killObelix'])
    
    #turnEverythingOff


