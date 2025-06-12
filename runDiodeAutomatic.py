import subprocess, signal
import time, datetime
import yaml
import argparse

## change the sensorName before starting anything!
# sensorName = 'P4665_4_A_typeE1'

# irradiationSteps = [0,1,2,5,10,20,40]
# # irradiationSteps = [0,0.5,1,2,3,4,5,7,10,15,20,25,30,35,40,50,70]

def runMeasurements(sensorName,targetDose,cmd,config,useStripCode=False):
    if useStripCode:
        return subprocess.run(['python', '.\main.py', 'Diode_{n}_m20C_{b}kGy'.format(n=sensorName, b=targetDose), cmd], check=True)
    return subprocess.run(['python', '.\main.py', 'Diode_{n}_m20C_{b}kGy'.format(n=sensorName, b=targetDose), cmd, '-c', config], check=True)

useStripCode = False

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, required=True, help="Path to the config file.")
args = parser.parse_args()

with open(args.config, 'r') as file:
    config = yaml.safe_load(file)

sensorName = config['sensorName']
irradiationSteps = config['irradiationSteps']


#cmd = 'testMD_DiodeStrip' if not useStripCode else 'testMD_fullStrip'
cmd = 'testEF_fullDiode'

try:
    for istep, step in enumerate(irradiationSteps[:-1]):

        ## this will run the pre-irradiation measurements
        if not istep and not step:
          measurements = runMeasurements(sensorName,step,cmd,args.config,useStripCode)
          #subprocess.run(['python', '.\main.py', 'Diode_{n}_m20C_{b}kGy'.format(n=sensorName, b=step), cmd, '-c', args.config], check=True)
    
        targetDose = irradiationSteps[istep+1]
        ## then first run the obelix irradiation step, followed by the measurements
        obelix       = subprocess.run(['python', '.\obelixControl_Strip.py', str(step), str(targetDose), 'yes'], check=True)
        #measurements = subprocess.run(['python', '.\main.py', 'Diode_{n}_m20C_{b}kGy'.format(n=sensorName, b=targetDose), cmd, '-c', args.config], check=True)
        measurements = runMeasurements(sensorName,targetDose,cmd,args.config,useStripCode)

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


