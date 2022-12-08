import matplotlib.pyplot as plt
import numpy as np

def main():
    # use ggplot style for more sophisticated visuals
    plt.style.use('ggplot')
    
    fig = plt.figure(figsize=(13,6))
    ax0= fig.add_subplot(121)
    ax1= fig.add_subplot(122)
    axs = [ax0, ax1]
    
    def live_plotter(x_vec,y1_data,line1,ind=0,identifier='',pause_time=0.5):
        if line1==[]:
            # this is the call to matplotlib that allows dynamic plotting
            plt.ion()
            #fig = plt.figure(figsize=(13,6))
            #ax = fig.add_subplot(111)
            # create a variable for the line so we can later update it
            line1, = axs[ind].plot(x_vec,y1_data,'-o',alpha=0.8)        
            #update plot label/title
            axs[ind].set_ylabel('Y Label')
            axs[ind].set_title('Title: {}'.format(identifier))
            plt.show()
        
        # after the figure, axis, and line are created, we only need to update the y-data
        line1.set_xdata(x_vec)
        line1.set_ydata(y1_data)
        # adjust limits if new data goes beyond bounds
        if np.min(x_vec)<=line1.axes.get_xlim()[0] or np.max(x_vec)>=line1.axes.get_xlim()[1]:
            axs[ind].set_xlim([np.min(x_vec)-np.std(x_vec),1.1*np.max(x_vec)+np.std(x_vec)])
    
        if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
            axs[ind].set_ylim([np.min(y1_data)-np.std(y1_data),1.1*np.max(y1_data)+np.std(y1_data)])
        # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
        plt.pause(pause_time)
        
        # return line so we can update it again in the next iteration
        return line1
    
    
    
    #size = 100
    #x_vec = np.linspace(0,1,size+1)[0:-1]
    #y_vec = np.random.randn(len(x_vec))
    #line1 = []
    #while True:
    #    rand_val = np.random.randn(1)
    #    y_vec[-1] = rand_val
    #    line1 = live_plotter(x_vec,y_vec,line1)
    #    y_vec = np.append(y_vec[1:],0.0)
    
    x_vec0, y_vec0 = [], []
    x_vec1, y_vec1 = [], []
    line0, line1   = [], []
    
    try:
        for i in range(10):
            x_vec0.append(i)
            y_vec0.append(i*2)
        
            line0 = live_plotter(x_vec0, y_vec0, line0)
    except KeyboardInterrupt:
        print('dodododo')
    
    try:
        for i in range(10):
            x_vec1.append(i)
            y_vec1.append(4+i*i*1.2-2.5*i)
            line1 = live_plotter(x_vec1, y_vec1, line1, ind=1)
    except KeyboardInterrupt:
        print('dodododo')

main()

