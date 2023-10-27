import subprocess, signal, time, datetime

today = datetime.date.today().isoformat()

## change the sensorName before starting anything!
sensorName     = '102183'
integratedDose = 700 ## in kGy

sleepTime = 3600*3

cmd = 'testMD_fullSensorMeasurements'

try:
    nAnnealing = 0
    while True:
        now = datetime.datetime.now()
        dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
        subprocess.run(['python', '.\main.py', '{n}_p0C_{b}kGy_p20CannealingStep{na}'.format(n=sensorName, b=integratedDose, na=nAnnealing), cmd], check=True)
        time.sleep(sleepTime)
        nAnnealing += 1
    

## if anything exits with anything other than exit(0), 
## we end up in the subprocess exception, and everything stops

except subprocess.CalledProcessError as e:
    print(e) ## print the exception

except KeyboardInterrupt:
    print('you stopped the program')
    pass
    #obelix = subprocess.run(['python', '.\obelixControl.py', 'killObelix'])
