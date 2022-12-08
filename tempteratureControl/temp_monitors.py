import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.lines
import mpld3, sys, datetime
from ke2001 import *
from sympy import Symbol
from sympy.solvers import solve

#matplotlib.use("Qt4agg")
plt.style.use('ggplot')
#matplotlib.rc('font',family='Arial')
pause_time = 2.000


def mypause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(interval)
            return


def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(15,5))
    ax0 = fig.add_subplot(131)
    ax1 = fig.add_subplot(132)
    ax2 = fig.add_subplot(133)

    return fig, ax0, ax1, ax2

def live_plotter(x_vec, y_vec, ax, line, identifier='', color='k',pause_time=0.001,title='',whichSignal=''):
    if line ==[]:
        if whichSignal == 'internal':
            line, = ax.plot(x_vec, y_vec, color='green', alpha=0.8,label = 'internal: %.02f C'%internal_temp)
            ax.legend(loc='upper left')
            #ax.text(5,3,'Internal Temp: %.02f' %internal_temp,fontsize=12)
        elif whichSignal == 'external':
            line, = ax.plot(x_vec, y_vec, color='orange', alpha=0.8, label = 'external: %.02f C'%external_temp)
            ax.legend(loc='upper left')
            #ax.text(5, 4,'External Temp Temp: %.02f' %external_temp,fontsize = 12)
        elif whichSignal == 'setpoint':
            line, = ax.plot(x_vec, y_vec, color='yellow', alpha=0.8, label = 'setpoint: %.02f C'%setpoint_temp)
            ax.legend(loc='upper left')
            #ax.text(5,5,'Setpoint: %.02f' %setpoint_temp,fontsize = 12)
        else:
            line, = ax.plot(x_vec, y_vec, color='blue', alpha=0.8, label = 'pt1000: %.02f C'%pt1000_temp)
            ax.legend(loc='upper left')
            #ax.text(5,7,'PT1000 Temp: %.02f' %pt1000_temp,fontsize=12)
        #update plot label/title
        ax.set_ylabel('Temperature (Celsius)')
        ax.set_xlabel('time (seconds)')
        ax.set_title(title)
        plt.show(block=False)

    else:
        if not -50. < y_vec[-1] < 100.:
            line.set_label('{n}: OFF'. format(n=whichSignal.replace('pt_','PT ')))
        else:
            line.set_label('{n}: {a:.2f}'. format(n=whichSignal.replace('pt_','PT '), a=y_vec[-1]))
        ax.legend(loc='upper left')

    line.set_xdata(x_vec)
    line.set_ydata(y_vec)
    ax.set_xlim([x_vec.min(),x_vec.max()])
    ax.set_ylim([-35,35])

    
##    if whichSignal == 'internal':
##        ax.legend('internal: %.02f C'%internal_temp,loc='upper left')
##    elif whichSignal == 'external':
##        ax.legend('external: %.02f C'%external_temp,loc='upper left')
##    elif whichSignal == 'setpoint':
##        ax.legend('setpoint: %.02f C'%setpoint_temp,loc='upper left')
##    else:
##        ax.legend('pt1000: %.02f C'%pt1000_temp,loc='upper left')
    
    # adjust limits if new data goes beyond bounds
    '''
    if np.min(y_vec)<=line.axes.get_ylim()[0] or np.max(y_vec)>=line.axes.get_ylim()[1]:
        ax.set_ylim([np.min(y_vec)-np.std(y_vec),np.max(y_vec)+np.std(y_vec)])
    '''
    '''
    if np.min(x_vec)<=line.axes.get_xlim()[0] or np.max(x_vec)>=line.axes.get_xlim()[1]:
        ax.set_xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])
    '''
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    
    #plt.pause(pause_time)
    return line

# orange external green internal



def R2T_PTX_ITS90(R,R0):
    #PTX (X=R0) calibration with ITS-90 standard
    t = Symbol('t')
    A = 3.9083E-3
    B = -5.7750E-7
    C = 0.
    if R > R0 : C = -4.183E-12
    T = solve(R-R0*(1+A*t+B*t*t+C*(t-100)*t*t*t),t)
    return T[0]




from softcheck.logic import Com
from softcheck.logic import CommunicationTimeout
from softcheck.pp_commands import PpCom
import time
com = Com("serial", 2.1,3)
com.open("COM9", 9600) #open COMX with 9600 (address not defined)
pp = PpCom(com)


x = np.array([])
maximumStepsBefore = 600
y = np.array([])
y2 = np.array([])
y3 = np.array([])
y4 = np.array([])
line  = []
line2 = []
line3 = []
line4 = []
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax2 = fig.add_subplot(111)
ax3 = fig.add_subplot(111)
ax4 = fig.add_subplot(111)
pt1000_connected = True
try:
    multimeter = ke2001(16)
    multimeter.reset()
    multimeter.set_sense('resistance')
    multimeter.set_terminal('rear')
    multimeter.set_nplc(10)
except:
    multimeter = 0
    pt1000_connected = False

#if not pt1000_connected:
#    inp = input('PT 1000 not found ... check your setup or type "yes" to move on without it.')

i = 0
plt.ion()
toggle_var = True

setpoint_temperature = 20
if len(sys.argv) > 1:
    setpoint_temperature = int(sys.argv[1])

#com.send('SP@{temp}\r\ni'.format(temp=int(setpoint_temperature*100)))
#com.send('TM@+0001\r\n')
#com.send('SP?\r\n')
#com.recv()
#a=input('user input required. arbitrary')
## marc com.send('TM@+0001\r\n')
## marc com.send('TM?\r\n')
## marc time.sleep(1)
## marc com.recv()

#'''

## marc com.send('SP@{temp}\r\n'.format(temp=int(setpoint_temperature*100)))
## marc com.send('SP?\r\n')
## marc com.recv()
## marc time.sleep(2)
## marc com.send('CA@+0001\r\n')
## marc com.send('CA?\r\n')
## marc com.recv()
## marc com.send('TM@+0001\r\n')
## marc com.send('TM?\r\n')
## marc com.recv()
## marc time.sleep(2)
#'''

initialTimeSec = time.time()
today = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
logfile = open('temperatureLogs/temperatureLog-{today}.dat'.format(today=today), 'w')#, buffering=1)
logfile.write('\t\t\tpt1000 - external - setpoint - internal\n')
logfile.flush()
while (True):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if multimeter:
            R = float(multimeter.read_resistance().split(',')[0].replace('OHM','').replace('N',''))
            pt1000_temp = R2T_PTX_ITS90(R,1000)
        else:
            print('PT 1000 not connected!')
            pt1000_temp = -999.
        internal_temp = pp.request_echo("TI")
        external_temp = pp.request_echo("TE")
        setpoint_temp = pp.request_echo('SP')
        internal_temp /= 100
        external_temp /= 100
        setpoint_temp /= 100

        if not i%20:
            logfile.write('{n}:\t{pt:.2f}\t{ex:.2f}\t{sp:.2f}\t{it:.2f}\n'.format(n=now, pt=pt1000_temp,ex=external_temp,sp=setpoint_temp,it=internal_temp))
            logfile.flush()
        
        
        if (i % maximumStepsBefore) == 0:
            if toggle_var:
                toggle_var = False
                #pp.send("SP",2000)
            else:
                toggle_var = True
                #pp.send('SP',1600)
        
        if i < (maximumStepsBefore + 2):
            x = np.concatenate((x,np.array([time.time() - initialTimeSec])))
            y = np.concatenate((y,np.array([internal_temp])))
            y2 = np.concatenate((y2,np.array([external_temp])))
            y3 = np.concatenate((y3,np.array([setpoint_temp])))
            y4 = np.concatenate((y4,np.array([pt1000_temp])))
        else:
            x = np.concatenate((x,np.array([time.time() - initialTimeSec])))
            x = x[1:]
            y = np.concatenate((y,np.array([internal_temp])))
            y = y[1:]
            y2 = np.concatenate((y2,np.array([external_temp])))
            y2 = y2[1:] 
            y3 = np.concatenate((y3,np.array([setpoint_temp])))
            y3 = y3[1:]
            y4 = np.concatenate((y4,np.array([pt1000_temp])))
            y4 = y4[1:]
        line = live_plotter(x,y,ax,line,pause_time=pause_time,title='Thermal Monitors',whichSignal='internal')
        line2 = live_plotter(x,y2,ax2,line2,pause_time=pause_time,title='Thermal Monitors',whichSignal='external')
        line3 = live_plotter(x,y3,ax3,line3,pause_time=pause_time,title='Thermal Monitors',whichSignal='setpoint')
        line4 = live_plotter(x,y4,ax4,line4,pause_time=pause_time,title='Thermal Monitors',whichSignal='pt_1000')
        mypause(1)
        i+=2   
    except:
        logfile.write('\n END: Keyboard Interrupt (or some other exception)\n\n')
        break
logfile.close()
#com.send('CA@+0000\r\n')

#pp.request("TI")
##pp.check_range("TI", 500, 6000)
##pp.request("TE")
##pp.check_range("TE", 0, 7000)
#p.change_to("CA", 1)
#time.sleep(20)
##pp.request("TP")
#pp.send("SP",  1000)
#
### to get the internal temperature:
#print('this is the internal temperature')
#p.request_echo("TI")
#print('this is the setpoint .... maybe')
#p.request_echo("SP")
#print('this is the external temperature')
#p.request_echo("TE")
#com.close()
