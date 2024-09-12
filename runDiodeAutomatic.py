import subprocess, signal
import time, datetime

## change the sensorName before starting anything!
sensorName = 'P4665_4_A_typeE1'

irradiationSteps = [0,1,2,5,10,20,40]
# irradiationSteps = [0,0.5,1,2,3,4,5,7,10,15,20,25,30,35,40,50,70]





cmd = 'testEF_fullDiode'

try:
    for istep, step in enumerate(irradiationSteps[:-1]):

        ## this will run the pre-irradiation measurements
        #if not istep and not step:
        #   subprocess.run(['python', '.\main.py', 'Diode_{n}_m20C_{b}kGy'.format(n=sensorName, b=step), cmd], check=True)
    
        targetDose = irradiationSteps[istep+1]
        ## then first run the obelix irradiation step, followed by the measurements
        obelix       = subprocess.run(['python', '.\obelixControl_Strip.py', str(step), str(targetDose), 'yes'], check=True)
        measurements = subprocess.run(['python', '.\main.py', 'Diode_{n}_m20C_{b}kGy'.format(n=sensorName, b=targetDose), cmd], check=True)

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


