import serial
import io
import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import datetime as dt
import serial


port = "COM7"
baudrate = 9600
timeout = 0.001
ser = serial.Serial(port,baudrate,timeout=timeout) # this should only be executed once
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
print(ser)
print('com3 is open', ser.isOpen())

sio.flush()    # it is buffering. required to get the data out *now*

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
xss = []
ys = []


# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Read temperature
    temp_c = ''
    while temp_c=='' or float(temp_c.split(":")[-1]) <= -50.0:
        time.sleep(0.001)
        temp_c = sio.read()

    temp_c = temp_c.split(":")[-1]

    # Add x and y to lists
    time_now = dt.datetime.now().strftime('%H:%M:%S.%f')
    xs.append(time_now)

    time_now = time_now.split(".")[0]
    xss.append(time_now)

    ys.append(float(temp_c))

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]
    
    ymin, ymax = min(ys), max(ys)
    yrange = ymax - ymin
    
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(ymin - yrange*0.1, ymax + yrange*0.1)

    # Draw x and y lists
    ax.plot(xs, ys, color="black")

    # Format plot
    plt.xticks(rotation=45, ha='right')

    # xsi = [x if i%2==0 else "" for i,x in enumerate(xss)]
    # ax.set(xticklabels=xsi)
    ax.set(xticklabels=[])

    plt.subplots_adjust(bottom=0.30)
    plt.title(f'Time: {time_now}')
    plt.ylabel('Temperature')
    plt.xlabel('Time')

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=10)
plt.show()

