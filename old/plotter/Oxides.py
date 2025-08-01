import os
import glob
import numpy as np
import natsort
import datetime

class Oxide:
  def __init__(self, name, length, folder, correction = None):
    self.name = name
    self.folder = folder
    self.length = length
    self.correction = correction
    

    self.time = []
    mint = int(datetime.datetime.now().timestamp())
    for f in sorted(glob.glob(self.folder+'*')):
        if(int(datetime.datetime.strptime(f.split('_')[-1][:-1], '%Y-%m-%d-%H-%M-%S').timestamp()) < mint):
           mint =  int(datetime.datetime.strptime(f.split('_')[-1][:-1], '%Y-%m-%d-%H-%M-%S').timestamp())

    self.startDate = mint

    for f in sorted(glob.glob(self.folder+'*')):
        self.time.append(int(datetime.datetime.strptime(f.split('_')[-1][:-1], '%Y-%m-%d-%H-%M-%S').timestamp())-self.startDate)
    self.time.sort()

    self.ivResults = []
    self.cvResults = []
    self.rvResults = []

    for f in natsort.natsorted(sorted(glob.glob(self.folder+'*'))):
        for f2 in sorted(glob.glob(f+'/*')):
            tempIV = []
            tempLCR = []
            for file in sorted(glob.glob(f2+'/*.dat')):
                nameFileSplit = file.split('\\')[3].split('_')
                if(nameFileSplit[0] == "iv"):
                    # Nominal Voltage [V]	 Measured Voltage [V]	Total current [A]	IS nominal voltage[V]	IS measured voltage[V]	IS current [A]	IS current Error [A]	Ramping PS current[A]
                    iv = np.loadtxt(file)
                    # bias voltage, IS voltage, IS current, IS current undertainty
                    tempIV.append([iv[:,1].tolist(), iv[:,4].tolist(), iv[:,5].tolist(), iv[:,6].tolist()])
                    #print(iv)

                elif(nameFileSplit[1] == "cv"):
                    # Nominal Voltage [V]	 Measured Voltage [V]	Freq [Hz]	R [Ohm]	R_Err [Ohm]	X [Ohm]	X_Err [Ohm]	Cs [F]	Cp [F]	Total Current [A]
                    cv = np.loadtxt(file)
                    # bias voltage, frequency, capacitance
                    
                    R_LCR = cv[:,3]
                    X_LCR = cv[:,5]
                    C_LCR = cv[:,8]
                    f_LCR = cv[:,2]

                    if(self.correction is not None):

                        
                        r_corrected = []
                        c_corrected = []

                        for i in range(len(cv[:,2])):
                            #X_LCR = -1/(2*np.pi*f_LCR[i]*C_LCR[i])
                            Z_LCR = R_LCR[i] + X_LCR[i]*1j

                            min_difference = float('inf')
                            for key in self.correction.keys():
                                difference = abs(key - f_LCR[i])
                                if difference < min_difference:
                                    min_difference = difference
                                    closest_key = key

                            Z_open = self.correction[closest_key][0][0] + self.correction[closest_key][0][1]*1j
                            Z_short = self.correction[closest_key][1][0] + self.correction[closest_key][1][1]*1j
                            Z_corrected = (Z_LCR-Z_short)/(1-(Z_LCR-Z_short)/Z_open)

                            C_corrected = C_LCR[i]+1/(2*np.pi*f_LCR[i]*self.correction[closest_key][0][1])

                            #print("Z Original: ", C_LCR[i], "Z Corrected: ", C_corrected)
                            #print("R Original: ", R_LCR[i], "R Nueva: ", np.real(Z_corrected), "C Original: ", C_LCR[i], "C Nueva: ", -1/(2*np.pi*f_LCR[i]*np.imag(Z_corrected)))
                            
                            c_corrected.append(C_corrected)
                            #r_corrected.append(np.real(Z_corrected))
                            #c_corrected.append(-1/(2*np.pi*f_LCR[i]*np.imag(Z_corrected)))
                        

                    else:
                        r_corrected = R_LCR.tolist()
                        c_corrected = C_LCR.tolist()

                    errorC = 1/(2*np.pi*cv[:,2]*(cv[:,5]**2))*cv[:,6]
                    #print(errorC)
                    tempLCR.append([cv[:,1].tolist(), cv[:,2].tolist(), c_corrected, errorC])

            #print("IV:", len(tempIV), "CV:", len(tempLCR))
            self.ivResults.append(tempIV)
            self.cvResults.append(tempLCR)

            #print(tempIV)
    self.ivResults = np.array(self.ivResults)
    #print("*************************************************")
    self.cvResults = np.array(self.cvResults)

    # order LCR results by frequency
    for d in range(len(self.cvResults)):
        self.cvResults[d] = self.cvResults[d][self.cvResults[d][:,1,0].argsort()]


    # order IV results by bias voltage
    for d in range(len(self.ivResults)):
        #print("****************************************")
        #print(self.ivResults[d])
        #print("****************************************")
        self.ivResults[d] = self.ivResults[d][self.ivResults[d][:,0,0].argsort()]
        
        #print(self.ivResults[d])
        #print("****************************************")
        tempRV = []
        for v in range(len(self.ivResults[d])):
            #print(self.ivResults[d,v])
            #print("****************************************")
            #print(self.ivResults[d,v,1])
            #print(self.ivResults[d,v,2])
            
            
            # Thanks ChatGPT 
            # Calculate weights based on uncertainties
            weights = 1.0 / self.ivResults[d,v,3]**2
            # Perform linear fit with weights
            coefficients, covariance = np.polyfit(self.ivResults[d,v,1], self.ivResults[d,v,2], deg=1, w=weights, cov=True)
            # Get the slope and intercept
            Gv, intercept = coefficients
            # Get the standard deviation of the slope (uncertainty in the slope)
            Gv_error = np.sqrt(covariance[0, 0])
            # Generate fit line
            Gv_line = np.polyval(coefficients, self.ivResults[d,v,1])

            rv_error = Gv_error/Gv**2
            rv = 1/Gv
            
            '''
            plt.errorbar(self.ivResults[d,v,1], self.ivResults[d,v,2], yerr=self.ivResults[d,v,3], fmt='o', label='Data with Error Bars')
            plt.plot(self.ivResults[d,v,1], rv_line, label=f'Weighted Linear Fit: y = {rv:.2f}x + {intercept:.2f}')
            plt.xlabel('X-axis')
            plt.ylabel('Y-axis')
            plt.legend()
            plt.show()
            print(rv_error)
            print(rv)
            '''
            
            #Bias V, resistance, uncertainty in resistance
            tempRV.append([self.ivResults[d,v,0,0], rv, rv_error, Gv, Gv_error, intercept])
        #print(tempRV)
        # time, Bias V, values
        self.rvResults.append(tempRV)


    self.rvResults = np.array(self.rvResults)
    #print(self.rvResults.shape)
    #np.save(self.name, self.rvResults)


    '''
    print("time, archivo, columna, fila")
    print(self.ivResults.shape)
    print(self.rvResults.shape)
    print(self.cvResults.shape)
    '''