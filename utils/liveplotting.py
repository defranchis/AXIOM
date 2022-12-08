## for live plotting
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mpld3

plt.style.use('ggplot')

def init_liveplot():
    plt.ion()
    fig = plt.figure(figsize=(15,5))
    ax0 = fig.add_subplot(131)
    ax1 = fig.add_subplot(132)
    ax2 = fig.add_subplot(133)

    return fig, ax0, ax1, ax2

def live_plotter(x_vec, y_vec, ax, line, identifier='', yaxis_title='', color='k',pause_time=0.1):
    if line ==[]:
        plt.ion()
        line, = ax.plot(x_vec, y_vec, color[0]+'-o', alpha=0.8)

        ax.set_title(identifier)
        #update plot label/title
        ax.set_ylabel(yaxis_title)
        ax.set_xlabel('voltage')
        plt.show()

    line.set_xdata(x_vec)
    line.set_ydata(y_vec)

    # adjust limits if new data goes beyond bounds
    if np.min(y_vec)<=line.axes.get_ylim()[0] or np.max(y_vec)>=line.axes.get_ylim()[1]:
        ax.set_ylim([np.min(y_vec)-np.std(y_vec),np.max(y_vec)+np.std(y_vec)])
    if np.min(x_vec)<=line.axes.get_xlim()[0] or np.max(x_vec)>=line.axes.get_xlim()[1]:
        ax.set_xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    return line

##def live_plotter(x_vec,y1_data,line1,identifier='',pause_time=0.1):
##    if line1==[]:
##        _init = True
##        # this is the call to matplotlib that allows dynamic plotting
##        plt.ion()
##        fig = plt.figure(figsize=(13,6))
##        ax = fig.add_subplot(111)
##        # create a variable for the line so we can later update it
##        line1, = ax.plot(x_vec,y1_data,'-o',alpha=0.8)        
##        #update plot label/title
##        plt.ylabel('current')
##        plt.title('Title: {}'.format(identifier))
##        plt.show()
##
##
##    # after the figure, axis, and line are created, we only need to update the y-data
##    line1.set_xdata(x_vec)   ## need to redraw also x axis
##    line1.set_ydata(y1_data) ## redraws y values
##
##    #line1, = ax.plot(x_vec,y1_data,'-o',alpha=0.8)        
##
##    # adjust limits if new data goes beyond bounds
##    if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
##        plt.ylim([np.min(y1_data)-np.std(y1_data),np.max(y1_data)+np.std(y1_data)])
##    if np.min(x_vec)<=line1.axes.get_xlim()[0] or np.max(x_vec)>=line1.axes.get_xlim()[1]:
##        plt.xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])
##    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
##    plt.pause(pause_time)
##
##    ## let's think about this later...
##    #if _init:
##    #    html_str = mpld3.fig_to_html(fig)
##    #    html_file= open("index.html","w")
##    #    html_file.write(html_str)
##    #    html_file.close()
##
##    
##    # return line so we can update it again in the next iteration
##    return line1

