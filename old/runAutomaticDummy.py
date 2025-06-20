import subprocess, signal


try:
    for istep, step in enumerate(range(3)):
    
        obelix = subprocess.run(['python', '.\\raise.py', '123234234'], check=True)
        #print(obelix.returncode)
        measurement = subprocess.run(['python', '.\\next.py' ], check=True)


except subprocess.CalledProcessError as e:
    print(e)
    #exit('something threw an error! hopefully you get some information out of the printouts')

except KeyboardInterrupt:
    print('sending keyboard interrupt to obelix')
    obelix.send_signal(signal.SIGINT)

