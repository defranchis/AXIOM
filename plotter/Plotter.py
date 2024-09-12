import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator
from matplotlib.cm import coolwarm, ScalarMappable
from matplotlib import gridspec
from matplotlib.pyplot import axhline, subplots, show, hist, figure, setp, colorbar, plot, cm, title, xlabel, ylabel, grid, legend, savefig, axes, pcolormesh, close
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator, MaxNLocator
import matplotlib.colors as colors
from matplotlib.lines import Line2D
import random

import numpy as np
import datetime, glob
import pandas as pd

from Oxides import Oxide

class Plotter:
    
    def __init__(self):
        self.route = "plotter/plots/"
        self.routeTemp = "temperatureLogs/"
        self.fig, self.ax1 = plt.subplots()
    

    def plotCV_freq(self, ox):
        for d in range(len(ox.cvResults)):
            self.fig, self.ax1 = plt.subplots()
            color = plt.cm.jet(np.linspace(0,1,len(ox.cvResults[d])))  
            for f in range(len(ox.cvResults[d])):
                self.ax1.errorbar(-ox.cvResults[d,f,0,:], ox.cvResults[d,f,2,:]/ox.length, yerr=ox.cvResults[d,f,3,:]/ox.length, fmt='o', color=color[f])
                self.ax1.plot(-ox.cvResults[d,f,0,:], ox.cvResults[d,f,2,:]/ox.length, label=(str(int(ox.cvResults[d,f,1,0]/1e3))+" kHz"), color=color[f])
            self.ax1.set_title(ox.name+" - time: "+str(str(datetime.timedelta(seconds=ox.time[d])))+"s", fontsize=16)
            self.ax1.set_ylabel("Capacitance / Length [F/cm]", fontsize=12)
            self.ax1.set_xlabel("Bias voltage [V]", fontsize=12)
            self.ax1.tick_params(axis='both', which='major', labelsize=11)
            self.ax1.tick_params(axis='both', which='minor', labelsize=11)
            #self.ax1.tick_params(axis='y', labelcolor=color)
            self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
            self.ax1.grid()
            #self.ax1.set_yscale('log')
            self.fig.tight_layout()
            plt.legend(loc="upper right", prop={'size': 12})
            #plt.show()
            self.fig.savefig(self.route+"capacitance/"+ox.name+"_"+str(ox.time[d])+"s_CV_Curve"+'.png')



    def plotCV_freq_multi(self, oxis, color, lines, markers, interestingFreqs, biasV, time):
        
        #color = plt.cm.jet(np.linspace(0,1,len(oxis)))
        fname = ""
        nVs = 0
        legend_elements = []
        for ox in oxis:
            if time in ox.time:
                valuesForF = []
                errorsForF = []
                for freq in interestingFreqs:
                    indextime = ox.time.index(time)
                    indexFreq = (np.abs(ox.cvResults[indextime, :, 1, 0] - freq)).argmin()
                    indexBiasV = (np.abs(ox.cvResults[indextime, indexFreq, 0,:] - biasV)).argmin()
                    valuesForF.append(ox.cvResults[indextime, indexFreq,2,indexBiasV])
                    errorsForF.append(ox.cvResults[indextime, indexFreq,3,indexBiasV])
                self.ax1.errorbar(interestingFreqs, np.array(valuesForF)/ox.length, yerr=np.array(errorsForF)/ox.length, fmt=markers[nVs], color=color[nVs])
                self.ax1.plot(interestingFreqs, np.array(valuesForF)/ox.length, label=(ox.name), color=color[nVs], linestyle=lines[nVs])
                legend_elements.append(Line2D([0], [0], c=color[nVs], marker=markers[nVs], label=ox.name))
                nVs+=1
                fname+=ox.name
                fname+=','
        self.ax1.set_title("Different thicknesses - Bias V: "+str(biasV)+"V - time: "+str(time)+"s", fontsize=16)
        self.ax1.set_ylabel("Capacitance / Length [F/cm]", fontsize=12)
        self.ax1.set_xlabel("Frequency [kHz]", fontsize=12)
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        self.ax1.set_xscale('log')
        self.fig.tight_layout()
        plt.legend(handles=legend_elements, loc="upper right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"capacitance/"+fname+"_"+str(biasV)+"V_"+str(time)+"s_fV_Curve"+'.png')
        plt.cla()



    def plotCV_multi(self, oxis, color, lines, markers, freq, time):
        
        self.fig, self.ax1 = plt.subplots()
        #color = plt.cm.jet(np.linspace(0,1,len(oxis))) 
        nOxis = 0
        fname = ""
        legend_elements = []
        for ox in oxis:
            if time in ox.time:
                indextime = ox.time.index(time)
                indexFreq = np.where(ox.cvResults[indextime] == freq)[0][0]
                self.ax1.errorbar(-ox.cvResults[indextime,indexFreq,0,:], ox.cvResults[indextime,indexFreq,2,:]/ox.length, yerr=ox.cvResults[indextime,indexFreq,3,:]/ox.length, fmt=markers[nOxis], color=color[nOxis])
                self.ax1.plot(-ox.cvResults[indextime,indexFreq,0,:], ox.cvResults[indextime,indexFreq,2,:]/ox.length, label=(ox.name), color=color[nOxis], linestyle=lines[nOxis])
                legend_elements.append(Line2D([0], [0], c=color[nOxis], marker=markers[nOxis], label=ox.name))
                nOxis +=1
            fname+=ox.name
            fname+=','
        self.ax1.set_title("Different thicknesses - time: "+str(time)+"s - Freq: "+str(int(freq/1e6))+"MHz", fontsize=16)
        self.ax1.set_ylabel("Capacitance / Length [F/cm]", fontsize=12)
        self.ax1.set_xlabel("Bias voltage [V]", fontsize=12)
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(handles=legend_elements, loc="lower right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"capacitance/"+fname+"_"+str(time)+"s_"+str(int(freq/1e6))+"MHz_CV_Curve"+'.png')
        plt.cla()


    def plotCtime(self, ox, freq, biasVs):
        
        self.fig, self.ax1 = plt.subplots()
        color = plt.cm.jet(np.linspace(0,1,len(biasVs))) 
        nVs = 0
        
        for v in biasVs:
            valuesFortime = []
            errorsFortime = []
            for d in range(len(ox.cvResults)):
                indexFreq = np.where(ox.cvResults[d] == freq)[0][0]
                indexBiasV = (np.abs(ox.cvResults[d, indexFreq, 0,:] - v)).argmin()
                valuesFortime.append(ox.cvResults[d,indexFreq,2,indexBiasV])
                errorsFortime.append(ox.cvResults[d,indexFreq,3,indexBiasV])
                #td = [datetime.timedelta(seconds=t) for t in ox.time]
            self.ax1.errorbar(ox.time, np.array(valuesFortime)/ox.length, yerr=np.array(errorsFortime)/ox.length, fmt='o', color=color[nVs])
            self.ax1.plot(ox.time, np.array(valuesFortime)/ox.length, label=(str(v)+"V"), color=color[nVs])
            nVs+=1
        self.ax1.set_title(ox.name+" - Freq: "+str(int(freq/1e3))+"MHz", fontsize=16)
        self.ax1.set_ylabel("Capacitance / Length [F/cm]", fontsize=12)
        self.ax1.set_xlabel("Time [s]", fontsize=12)
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(loc="upper right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"capacitance/"+ox.name+"_"+str(int(freq/1e6))+"MHz_CT_Curve"+'.png')
        plt.cla()

    
    def plotCtime_multi(self, oxis, color, lines, markers, freq, biasV):
        
        self.fig, self.ax1 = plt.subplots()
        #color = plt.cm.jet(np.linspace(0,1,len(oxis))) 
        fname = ""
        nVs = 0
        legend_elements = []
        for ox in oxis:
            #print(ox.name)
            valuesFortime = []
            errorsFortime = []
            for d in range(len(ox.cvResults)):


                #print(d)
                indexFreq = np.where(ox.cvResults[d] == freq)[0][0]
                indexBiasV = (np.abs(ox.cvResults[d, indexFreq, 0,:] - biasV)).argmin()
                if np.abs(ox.cvResults[d, indexFreq, 0, indexBiasV] - biasV) > 110:
                    raise Exception("Voltage not found")
                valuesFortime.append(ox.cvResults[d,indexFreq,2,indexBiasV])
                errorsFortime.append(ox.cvResults[d,indexFreq,3,indexBiasV])
                
                
                
            #print(ox.name, ox.time, np.array(valuesFortime), np.array(errorsFortime))

            self.ax1.errorbar(ox.time, np.array(valuesFortime)/ox.length, yerr=np.array(errorsFortime)/ox.length, fmt=markers[nVs], color=color[nVs])
            self.ax1.plot(ox.time, np.array(valuesFortime)/ox.length, label=(ox.name), color=color[nVs], linestyle=lines[nVs])
            legend_elements.append(Line2D([0], [0], c=color[nVs], marker=markers[nVs], label=ox.name))
            nVs+=1
            fname+=ox.name
            fname+=','
        self.ax1.set_title("Different thicknesses - Bias V: "+str(biasV)+"V - Freq: "+str(int(freq/1e6))+"MHz", fontsize=16)
        self.ax1.set_ylabel("Capacitance / Length [F/cm]", fontsize=12)
        self.ax1.set_xlabel("Time [s]", fontsize=12)
        #self.ax1.set_ylim([3.5e-13, 4.3e-13])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(handles=legend_elements, loc="upper right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"capacitance/"+fname+"_"+str(biasV)+"V_"+str(int(freq/1e6))+"MHz_CT_Curve"+'.png')
        plt.cla()
    


    '''
    RESISTANCES
    '''

    def plotRV(self, ox):
        self.fig, self.ax1 = plt.subplots()
        color = plt.cm.jet(np.linspace(0,1,len(ox.rvResults)))
        for d in range(len(ox.rvResults)):
            self.ax1.errorbar(-ox.rvResults[d,:,0], ox.rvResults[d,:,1]*ox.length, yerr=ox.rvResults[d,:,2]*ox.length, fmt='o', color=color[d])
            self.ax1.plot(-ox.rvResults[d,:,0], ox.rvResults[d,:,1]*ox.length, color=color[d], label=(str(str(datetime.timedelta(seconds=ox.time[d])))+"s"))
        #self.ax1.hlines(y=1.22e3, xmin=0, xmax=ox.time[-1]*1.02, linewidth=2, color='r', linestyle="dashed")
        self.ax1.set_title(ox.name, fontsize=16)
        self.ax1.set_ylabel("Resistance · Length [Ω·cm]", fontsize=12)
        self.ax1.set_xlabel("Bias voltage [V]", fontsize=12)
        self.ax1.set_ylim([5e7, 1e9])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(loc="lower right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"resistance/"+ox.name+"_RV_Curve"+'.png')
        plt.cla()



    def plotRV_multi(self, oxis, color, lines, markers, time):
        
        self.fig, self.ax1 = plt.subplots()
        #color = plt.cm.jet(np.linspace(0,1,len(oxis))) 
        nOxis = 0
        fname = ""
        legend_elements = []
        for ox in oxis:
            if time in ox.time:
                indextime = ox.time.index(time)
                self.ax1.errorbar(-ox.rvResults[indextime,:,0], ox.rvResults[indextime,:,1]*ox.length, yerr=ox.rvResults[indextime,:,2]*ox.length, fmt=markers[nOxis], color=color[nOxis], linestyle=lines[nOxis])
                self.ax1.plot(-ox.rvResults[indextime,:,0], ox.rvResults[indextime,:,1]*ox.length, color=color[nOxis], label=(ox.name))
                legend_elements.append(Line2D([0], [0], c=color[nOxis], marker=markers[nOxis], label=ox.name))
                nOxis +=1
            fname+=ox.name
            fname+=','
        self.ax1.set_title("Different thicknesses - time: "+str(time)+"s", fontsize=16)
        self.ax1.set_ylabel("Resistance · Length [Ω·cm]", fontsize=12)
        self.ax1.set_xlabel("Bias voltage [V]", fontsize=12)
        self.ax1.set_ylim([5e7, 5e9])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(handles=legend_elements, loc="upper right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"resistance/"+fname+"_"+str(time)+"s_RV_Curve"+'.png')
        plt.cla()


    def plotRtime(self, ox, biasVs):
        
        self.fig, self.ax1 = plt.subplots()
        color = plt.cm.magma(np.linspace(0.1,0.9,len(biasVs))) 
        nVs = 0
        legend_elements = []
        markers = ['o', 'v', '^', 's', 'P', '*', 'X']
        for v in biasVs:
            valuesFortime = []
            uncertaintyFortime = []
            for d in range(len(ox.rvResults)):
                indexBiasV = (np.abs(ox.rvResults[d,:,0] - v)).argmin()
                valuesFortime.append(ox.rvResults[d,indexBiasV,1])
                uncertaintyFortime.append(ox.rvResults[d,indexBiasV,2])
            self.ax1.errorbar( [x / 3600/24 for x in ox.time], np.array(valuesFortime)*ox.length, yerr=np.array(uncertaintyFortime)*ox.length, fmt=markers[nVs], color=color[nVs])
            self.ax1.plot([x / 3600/24 for x in ox.time], np.array(valuesFortime)*ox.length, color=color[nVs], label=(str(v)+"V"))
            legend_elements.append(Line2D([0], [0], c=color[nVs], marker=markers[nVs], label=(str(v)+"V")))
            nVs+=1
        #self.ax1.hlines(y=1.22e3, xmin=0, xmax=ox.time[-1]*1.02, linewidth=2, color='r', linestyle="dashed")
        self.ax1.set_title("Resistance vs. Time - " + ox.name, fontsize=16)
        self.ax1.set_ylabel("Resistance · Length [Ω·cm]", fontsize=12)
        self.ax1.set_xlabel("Time [days]", fontsize=12)
        #self.ax1.set_ylim([5e7, 1e9])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        self.ax1.set_xlim([0, ox.time[-1]*1.02/3600/24])
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(handles=legend_elements, loc="upper left", prop={'size': 12})
        #plt.legend(loc="upper right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"resistance/"+ox.name+"_RT_Curve"+'.png')
        plt.cla()




    def plotRtime_multi(self, oxis, color, lines, markers, biasV):
        
        self.fig, self.ax1 = plt.subplots()
        #color = plt.cm.jet(np.linspace(0,1,len(oxis)))
        fname = ""
        nOxis = 0
        legend_elements = []
        for ox in oxis:
            valuesFortime = []
            uncertaintyFortime = []


         



            for d in range(len(ox.rvResults)):
                indexBiasV = (np.abs(ox.rvResults[d,:,0] - biasV)).argmin()
                valuesFortime.append(ox.rvResults[d,indexBiasV,1])
                uncertaintyFortime.append(ox.rvResults[d,indexBiasV,2])

            if (ox.name == "Type E1 (1)" and biasV == -600):
                index = ox.time.index(30)
                ox.time.remove(ox.time[index])
                valuesFortime.remove(valuesFortime[index])
                uncertaintyFortime.remove(uncertaintyFortime[index])

            self.ax1.errorbar(ox.time, np.array(valuesFortime)*ox.length, yerr=np.array(uncertaintyFortime)*ox.length, fmt=markers[nOxis], color=color[nOxis], linestyle=lines[nOxis])
            self.ax1.plot(ox.time, np.array(valuesFortime)*ox.length, color=color[nOxis], label=(ox.name))
            legend_elements.append(Line2D([0], [0], c=color[nOxis], marker=markers[nOxis], label=ox.name))
            nOxis+=1
            fname+=ox.name
            fname+=','
        self.ax1.set_title("Different thicknesses - Bias V: "+str(biasV)+"V", fontsize=16)
        #self.ax1.set_title("300um Type C oxide @ 14.3 s/h (150mm height)", fontsize=14)
        self.ax1.set_ylabel("Resistance · Length [Ω·cm]", fontsize=12)
        self.ax1.set_xlabel("Time [s]", fontsize=12)
        self.ax1.set_ylim([5e7, 1e12])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(handles=legend_elements, loc="upper left", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"resistance/"+fname+"_"+str(biasV)+"V_RT_Curve"+'.png')
        plt.cla()



    '''
    IVs
    '''

    

    def plotIV_Bias(self, ox, time, biasV):
        
        self.fig, self.ax1 = plt.subplots()
        color = plt.cm.jet(np.linspace(0,1,len(biasV)))
        for v in range(len(biasV)):
            indextime = ox.time.index(time)
            indexBiasV = (np.abs(ox.ivResults[indextime,:,0,0] - biasV[v])).argmin()
            self.ax1.errorbar(ox.ivResults[indextime,indexBiasV,1,:], ox.ivResults[indextime,indexBiasV,2,:], yerr=ox.ivResults[indextime,indexBiasV,3,:], fmt='o', color=color[v])
            self.ax1.plot(ox.ivResults[indextime,indexBiasV,1,:], ox.ivResults[indextime,indexBiasV,2,:], color=color[v], label=(str(biasV[v])+"V"))

            Gv_line = np.polyval([ox.rvResults[indextime,indexBiasV,3], ox.rvResults[indextime,indexBiasV,5]], ox.ivResults[indextime,indexBiasV,1,:])
            self.ax1.plot(ox.ivResults[indextime,indexBiasV,1,:], Gv_line, color=color[v], linestyle = 'dashed')



        self.ax1.set_title(ox.name+" - time: "+str(time)+"s", fontsize=16)
        self.ax1.set_ylabel("Interstrip current [A]", fontsize=12)
        self.ax1.set_xlabel("Interstrip voltage [V]", fontsize=12)
        #self.ax1.set_ylim([-5e-10, 5e-10])
        #self.ax1.set_ylim([0.5e8, 1e12])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(loc="lower right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"current/"+str(ox.name)+"_"+str(time)+"s_IV_Curve"+'.png')
        plt.cla()


    def plotIV_time(self, ox, time, biasV):
        
        self.fig, self.ax1 = plt.subplots()
        color = plt.cm.jet(np.linspace(0,1,len(time)))
        for d in range(len(time)):
            indextime = ox.time.index(time[d])
            indexBiasV = (np.abs(ox.ivResults[indextime,:,0,0] - biasV)).argmin()
            self.ax1.errorbar(ox.ivResults[indextime,indexBiasV,1,:], ox.ivResults[indextime,indexBiasV,2,:], yerr=ox.ivResults[indextime,indexBiasV,3,:], fmt='o', color=color[d])
            self.ax1.plot(ox.ivResults[indextime,indexBiasV,1,:], ox.ivResults[indextime,indexBiasV,2,:], color=color[d], label=(str(time[d])+"s"))
            Gv_line = np.polyval([ox.rvResults[indextime,indexBiasV,3], ox.rvResults[indextime,indexBiasV,5]], ox.ivResults[indextime,indexBiasV,1,:])
            self.ax1.plot(ox.ivResults[indextime,indexBiasV,1,:], Gv_line, color=color[d], linestyle = 'dashed')
        self.ax1.set_title(ox.name+" - Bias voltage: "+str(biasV)+"V", fontsize=16)
        self.ax1.set_ylabel("Interstrip current [A]", fontsize=12)
        self.ax1.set_xlabel("Interstrip voltage [V]", fontsize=12)
        #self.ax1.set_ylim([-5e-10, 5e-10])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        self.ax1.grid()
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()
        plt.legend(loc="lower right", prop={'size': 12})
        #plt.show()
        self.fig.savefig(self.route+"current/"+str(ox.name)+"_"+str(biasV)+"V_IV_Curve"+'.png')
        plt.cla()







    '''
    Temp
    '''


    def plotT_time(self, ox):
        
        self.fig, self.ax1 = plt.subplots()

        listDates = []
        for f in sorted(glob.glob(self.routeTemp+'/*.dat')):
            if(f.split('_')[1:]):
                listDates.append(datetime.datetime.strptime(f.split('_')[1:][0][:-4], '%Y-%m-%d-%H-%M-%S'))

        lastValidDate = min(listDates, key=lambda x: (x>datetime.datetime.fromtimestamp(int(ox.startDate)), abs(x-datetime.datetime.fromtimestamp(int(ox.startDate)))) )
        
        for f in sorted(glob.glob(self.routeTemp+'/*.dat')):
            if(lastValidDate.strftime('%Y-%m-%d-%H-%M-%S') in f.split('_')[1:][0]):
                with open(f) as fileOpen:
                    next(fileOpen)
                    arrayAllTemps = []
                    arrayMeasuredTemps = []
                    for line in fileOpen:
                        columns = line.split()  # Split by spaces
                        if(len(columns)==6):
                            arrayAllTemps.append([datetime.datetime.strptime(columns[0]+'-'+columns[1], '%Y-%m-%d-%H:%M:%S'), float(columns[2])])
                    
                    for entry in arrayAllTemps:
                        if lastValidDate <= entry[0] and datetime.datetime.fromtimestamp(int(ox.startDate))+datetime.timedelta(seconds=int(ox.time[-1])) >= entry[0]:
                            arrayMeasuredTemps.append([int(entry[0].timestamp())-int(lastValidDate.timestamp()), entry[1]])

                    arrayMeasuredTemps = np.array(arrayMeasuredTemps)
                    self.ax1.plot(arrayMeasuredTemps[:,0], arrayMeasuredTemps[:,1], linestyle = 'solid', label="Temperature evolution")

                    measurementDates = [min(arrayMeasuredTemps[:,0], key=lambda x: (x>t, abs(x-t))) for t in ox.time]
                    measurementTemperaturesIndex = np.in1d(arrayMeasuredTemps[:,0], measurementDates).nonzero()[0]
                    measurementTemperatures = [arrayMeasuredTemps[i,1] for i in measurementTemperaturesIndex]
                    self.ax1.plot(measurementDates, measurementTemperatures, 'x', color = 'red', label="Measurement taken")

                    self.ax1.set_title(ox.name+" - Temperature evolution", fontsize=16)
                    self.ax1.set_ylabel("Temperature [C]", fontsize=12)
                    self.ax1.set_xlabel("Time [s]", fontsize=12)
                    #self.ax1.set_ylim([-5e-10, 5e-10])
                    #self.ax1.set_ylim([0.5e8, 1e12])
                    self.ax1.tick_params(axis='both', which='major', labelsize=11)
                    self.ax1.tick_params(axis='both', which='minor', labelsize=11)
                    #self.ax1.tick_params(axis='y', labelcolor=color)
                    self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,2))
                    self.ax1.grid()
                    self.fig.tight_layout()
                    plt.legend(loc="lower right", prop={'size': 12})
                    self.fig.savefig(self.route+"temp/"+ox.name+"temp_Curve"+'.png')
                    plt.cla()



                    self.ax1.plot(measurementDates, measurementTemperatures, label="Measurement taken")

                    self.ax1.set_title(ox.name+" - Temperature evolution (measurements)", fontsize=16)
                    self.ax1.set_ylabel("Temperature [C]", fontsize=12)
                    self.ax1.set_xlabel("Time [s]", fontsize=12)
                    #self.ax1.set_ylim([-5e-10, 5e-10])
                    #self.ax1.set_ylim([0.5e8, 1e12])
                    self.ax1.tick_params(axis='both', which='major', labelsize=11)
                    self.ax1.tick_params(axis='both', which='minor', labelsize=11)
                    #self.ax1.tick_params(axis='y', labelcolor=color)
                    self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,2))
                    self.ax1.grid()
                    self.fig.tight_layout()
                    plt.legend(loc="lower right", prop={'size': 12})
                    self.fig.savefig(self.route+"temp/"+ox.name+"temp_Curve_meas"+'.png')
                    plt.cla()





    def plotTRSame_time(self, ox, biasVs):
        
        self.fig, self.ax1 = plt.subplots()



        color = plt.cm.magma(np.linspace(0.1,0.9,len(biasVs))) 
        nVs = 0
        legend_elements = []
        markers = ['o', 'v', '^', 's', 'P', '*', 'X']
        for v in biasVs:
            valuesFortime = []
            uncertaintyFortime = []
            for d in range(len(ox.rvResults)):
                indexBiasV = (np.abs(ox.rvResults[d,:,0] - v)).argmin()
                valuesFortime.append(ox.rvResults[d,indexBiasV,1])
                uncertaintyFortime.append(ox.rvResults[d,indexBiasV,2])
            self.ax1.errorbar( [x / 60 for x in ox.time], np.array(valuesFortime)*ox.length, yerr=np.array(uncertaintyFortime)*ox.length, fmt=markers[nVs], color=color[nVs])
            self.ax1.plot([x / 60 for x in ox.time], np.array(valuesFortime)*ox.length, color='blue', label="Resistance")
            nVs+=1
        #self.ax1.hlines(y=1.22e3, xmin=0, xmax=ox.time[-1]*1.02, linewidth=2, color='r', linestyle="dashed")
        
        self.ax1.set_ylabel("Resistance · Length [Ω·cm]", fontsize=12)
        self.ax1.set_xlabel("Time [min]", fontsize=12)
        #self.ax1.set_ylim([5e7, 1e9])
        self.ax1.tick_params(axis='both', which='major', labelsize=11)
        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
        #self.ax1.tick_params(axis='y', labelcolor=color)
        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        #self.ax1.grid()
        self.ax1.set_xlim([0, ox.time[-1]*1.02/60])
        #self.ax1.set_yscale('log')
        self.fig.tight_layout()




        ax2 = self.ax1.twinx()


        listDates = []
        for f in sorted(glob.glob(self.routeTemp+'/*.dat')):
            if(f.split('_')[1:]):
                listDates.append(datetime.datetime.strptime(f.split('_')[1:][0][:-4], '%Y-%m-%d-%H-%M-%S'))

        lastValidDate = min(listDates, key=lambda x: (x>datetime.datetime.fromtimestamp(int(ox.startDate)), abs(x-datetime.datetime.fromtimestamp(int(ox.startDate)))) )
        
        for f in sorted(glob.glob(self.routeTemp+'/*.dat')):
            if(lastValidDate.strftime('%Y-%m-%d-%H-%M-%S') in f.split('_')[1:][0]):
                with open(f) as fileOpen:
                    next(fileOpen)
                    arrayAllTemps = []
                    arrayMeasuredTemps = []
                    for line in fileOpen:
                        columns = line.split()  # Split by spaces
                        if(len(columns)==6):
                            arrayAllTemps.append([datetime.datetime.strptime(columns[0]+'-'+columns[1], '%Y-%m-%d-%H:%M:%S'), float(columns[2])])
                    
                    for entry in arrayAllTemps:
                        if lastValidDate <= entry[0] and datetime.datetime.fromtimestamp(int(ox.startDate))+datetime.timedelta(seconds=int(ox.time[-1])) >= entry[0]:
                            arrayMeasuredTemps.append([int(entry[0].timestamp())-int(lastValidDate.timestamp()), entry[1]])

                    arrayMeasuredTemps = np.array(arrayMeasuredTemps)

                    measurementDates = [min(arrayMeasuredTemps[:,0], key=lambda x: (x>t, abs(x-t))) for t in ox.time]
                    measurementTemperaturesIndex = np.in1d(arrayMeasuredTemps[:,0], measurementDates).nonzero()[0]
                    measurementTemperatures = [arrayMeasuredTemps[i,1] for i in measurementTemperaturesIndex]
                    ax2.plot([x / 60 for x in measurementDates], measurementTemperatures, color = 'red', label="Temperature")


                    ax2.set_title(ox.name+" - T-R (measurements)", fontsize=16)
                    ax2.set_ylabel("Temperature [C]", fontsize=12)
                    #ax2.set_ylim([-5e-10, 5e-10])
                    #ax2.set_ylim([0.5e8, 1e12])
                    ax2.tick_params(axis='both', which='major', labelsize=11)
                    ax2.tick_params(axis='both', which='minor', labelsize=11)
                    #ax2.tick_params(axis='y', labelcolor=color)
                    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,2))
                    #ax2.grid()
                    self.fig.tight_layout()
                    plt.legend(loc="lower right", prop={'size': 12})
                    self.fig.savefig(self.route+"temp/"+ox.name+"TR"+'.png')
                    plt.cla()




    def plotTR(self, ox, biasVs):
        
        self.fig, self.ax1 = plt.subplots()



        color = plt.cm.magma(np.linspace(0.1,0.9,len(biasVs))) 
        nVs = 0
        legend_elements = []
        markers = ['o', 'v', '^', 's', 'P', '*', 'X']
        for v in biasVs:
            valuesFortime = []
            uncertaintyFortime = []
            for d in range(len(ox.rvResults)):
                indexBiasV = (np.abs(ox.rvResults[d,:,0] - v)).argmin()
                valuesFortime.append(ox.rvResults[d,indexBiasV,1])
                uncertaintyFortime.append(ox.rvResults[d,indexBiasV,2])
            #self.ax1.errorbar( [x / 60 for x in ox.time], np.array(valuesFortime)*ox.length, yerr=np.array(uncertaintyFortime)*ox.length, fmt=markers[nVs], color=color[nVs])
            #self.ax1.plot([x / 60 for x in ox.time], np.array(valuesFortime)*ox.length, color='blue', label="Resistance")
            nVs+=1



            listDates = []
            for f in sorted(glob.glob(self.routeTemp+'/*.dat')):
                if(f.split('_')[1:]):
                    listDates.append(datetime.datetime.strptime(f.split('_')[1:][0][:-4], '%Y-%m-%d-%H-%M-%S'))

            lastValidDate = min(listDates, key=lambda x: (x>datetime.datetime.fromtimestamp(int(ox.startDate)), abs(x-datetime.datetime.fromtimestamp(int(ox.startDate)))) )
            
            for f in sorted(glob.glob(self.routeTemp+'/*.dat')):
                if(lastValidDate.strftime('%Y-%m-%d-%H-%M-%S') in f.split('_')[1:][0]):
                    with open(f) as fileOpen:
                        next(fileOpen)
                        arrayAllTemps = []
                        arrayMeasuredTemps = []
                        for line in fileOpen:
                            columns = line.split()  # Split by spaces
                            if(len(columns)==6):
                                arrayAllTemps.append([datetime.datetime.strptime(columns[0]+'-'+columns[1], '%Y-%m-%d-%H:%M:%S'), float(columns[2])])
                        
                        for entry in arrayAllTemps:
                            if lastValidDate <= entry[0] and datetime.datetime.fromtimestamp(int(ox.startDate))+datetime.timedelta(seconds=int(ox.time[-1])) >= entry[0]:
                                arrayMeasuredTemps.append([int(entry[0].timestamp())-int(lastValidDate.timestamp()), entry[1]])

                        arrayMeasuredTemps = np.array(arrayMeasuredTemps)

                        measurementDates = [min(arrayMeasuredTemps[:,0], key=lambda x: (x>t, abs(x-t))) for t in ox.time]
                        measurementTemperaturesIndex = np.in1d(arrayMeasuredTemps[:,0], measurementDates).nonzero()[0]
                        measurementTemperatures = [arrayMeasuredTemps[i,1] for i in measurementTemperaturesIndex]
                        self.ax1.scatter(measurementTemperatures, np.array(valuesFortime)*ox.length, color = 'red', label="Temperature")


                        self.ax1.set_title(ox.name+" - T-R (measurements)", fontsize=16)
                        self.ax1.set_ylabel("Resistance · Length [Ω·cm]", fontsize=12)
                        self.ax1.set_xlabel("Temperature [C]", fontsize=12)
                        #self.ax1.set_ylim([-5e-10, 5e-10])
                        #self.ax1.set_ylim([0.5e8, 1e12])
                        self.ax1.tick_params(axis='both', which='major', labelsize=11)
                        self.ax1.tick_params(axis='both', which='minor', labelsize=11)
                        #self.ax1.tick_params(axis='y', labelcolor=color)
                        self.ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,2))
                        self.ax1.grid()
                        self.fig.tight_layout()
                        plt.legend(loc="lower right", prop={'size': 12})
                        self.fig.savefig(self.route+"temp/"+ox.name+"-TR-"+str(v)+'.png')
                        plt.cla()







        





def nearest(self, items, pivot):
    return min(items, key=lambda x: abs(x - pivot))