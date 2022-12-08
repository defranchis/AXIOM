import subprocess, signal

## change the sensorName before starting anything!
sensorName = 'N4789-12_UL'

irradiationSteps = [0, 1, 2, 5, 10, 20, 40, 70, 100, 200, 300, 500, 700, 1000, 1500, 2000, 2500, 3000]
cmd = 'testMD_fullSensorMeasurements'

try:
    for istep, step in enumerate(irradiationSteps[:-1]):

        ## this will run the pre-irradiation measurements
        if not istep and not step:
            subprocess.run(['python', '.\main.py', '{n}_m20C_{b}kGy'.format(n=sensorName, b=step), cmd], check=True)
    
        targetDose = irradiationSteps[istep+1]
        ## then first run the obelix irradiation step, followed by the measurements
        obelix       = subprocess.run(['python', '.\obelixControl.py', str(step), str(targetDose), 'yes'], check=True)
        measurements = subprocess.run(['python', '.\main.py', '{n}_m20C_{b}kGy'.format(n=sensorName, b=targetDose), cmd], check=True)

## if anything exits with anything other than exit(0), 
## we end up in the subprocess exception, and everything stops
except subprocess.CalledProcessError as e:
    print(e) ## print the exception
    #if e == KeyboardInterrupt:
    #obelix       .send_signal(signal.SIGINT)
    #measurements .send_signal(signal.SIGINT)
    ## write an email to matteo

except KeyboardInterrupt:
    obelix = subprocess.run(['python', '.\obelixControl.py', 'killObelix'])
    
    #turnEverythingOff
