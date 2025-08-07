import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.lines
import mpld3, sys, datetime
import devices
from sympy import Symbol
from sympy.solvers import solve

# matplotlib.use("Qt4agg")
plt.style.use('ggplot')
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

    
    return line

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
com.open("COM10", 9600) #open COMX with 9600 (address not defined)
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
ax = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)
pt1000_connected = True
try:
    multimeter = devices.ke2001(16)
    multimeter.reset()
    multimeter.set_sense('resistance')
    multimeter.set_terminal('rear')
    multimeter.set_nplc(10)
except:
    multimeter = 0
    pt1000_connected = False

i = 0
plt.ion()
toggle_var = True

setpoint_temperature = 20
if len(sys.argv) > 1:
    setpoint_temperature = int(sys.argv[1])


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

