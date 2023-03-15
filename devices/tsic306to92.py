import io
import serial
import time
from pyvisa_device import device
from utils import logging
import datetime as dt
import matplotlib.pyplot as plt

class TSIC306TO92(device):
    """
    TSIC306TO92 temperature sensor.

    Example:
    -------------

    """


    def __init__(self, port="COM7", verbose=3):
        log = logging.setup_logger(__file__, verbose)

        log.info("Initialising device.")

        self.port = port
        self.baudrate = 9600
        self.timeout = 0.001
        self.ser = serial.Serial(self.port,self.baudrate,timeout=self.timeout) # this should only be executed once
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        if self.ser.isOpen():
            log.info('TSIC306TO92 is open')
        else:
            log.warning('Failed to open TSIC306TO92')

        self.sio.flush()    # it is buffering. required to get the data out *now*


    def create_figure(self):
        plt.ion()

        # Create figure for plotting
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.xs = []
        self.xss = []
        self.ys = []

        # Format plot
        self.ax.set(xticklabels=[])

        plt.ylabel('Temperature')
        plt.xlabel('Time')
        plt.subplots_adjust(bottom=0.1)

    # This function is called periodically from FuncAnimation
    def update_figure(self, temperature=None, target_temperature=-20, time_now=None):

        # Add x and y to lists
        if temperature is None:
            temperature = self.read_temperature()
        if time_now is None:
            time_now = dt.datetime.now().strftime('%H:%M:%S.%f')

        self.ys.append(temperature)
        self.xs.append(time_now)

        time_now = time_now.split(".")[0]
        self.xss.append(time_now)

        # Limit x and y lists to 20 items
        self.xs = self.xs[-1500:]
        self.ys = self.ys[-1500:]
        
        ymin, ymax = min(self.ys), max(self.ys)
        yrange = ymax - ymin
        
        self.ax.set_xlim(self.xs[0], self.xs[-1])
        self.ax.set_ylim(ymin - yrange*0.1, ymax + yrange*0.1)

        self.ax.plot([min(self.xs),max(self.xs)], [target_temperature, target_temperature], linestyle="--", color="black")
        
        # Draw x and y lists                          
        self.ax.plot(self.xs, self.ys, color="black")

        plt.title(f'Time: {time_now}')
        
        # drawing updated values
        self.fig.canvas.draw()
    
        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        self.fig.canvas.flush_events()
    
        # Set attribute functions
        # ---------------------------------






    # Read attribute functions
    # ---------------------------------
    def read_temperature(self):
        self.sio.flush()
        temp_c = ''
        while temp_c=='' or float(temp_c.split(":")[-1]) <= -50.0 or float(temp_c.split(":")[-1]) > 100:
            time.sleep(0.001)
            temp_c = self.sio.read()

        return float(temp_c.split(":")[-1])
