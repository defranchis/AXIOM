#!/usr/bin/python
import numpy as np
from optparse import OptionParser


## Constants
kBoltzmann = 8.61733 * 10**(-5) # [ev/K]
kZero = 273.15 # K



## Definitions
def correct_temperature(i, t):
    t += kZero 
    i_20 = i * (293.15/t)**2 * np.exp((-1) * 1.21/(2*kBoltzmann) * (t-293.15)/(t*293.15))
    return i_20


def read_file(fn):
    dat = np.loadtxt(fn, dtype='float', comments='#')
    return dat


def read_header(fn):
    hd = ''
    with open(fn) as f:
        next(f)
        for line in f:
            if line[0] == '#':
                if line[1:8] == 'HexPlot':
                    pass
                elif line[1:8] == 'Voltage':
                    pass
                elif line[1:4] == '[V]':
                    pass
                else:
                    hd += line.rstrip() + "\n"
    return hd


def process_file(dat, fInvert, fCorrect):
    out = []
    for line in dat:
        v = line[0]
        ch = line[1]
        curr = line[2]
        curr_err = line[3]
        tot_curr = line[4]
        v_msr = line[5]
        temp = line[7]
        hum = line[8]
        
        if (fInvert and fCorrect):
            v_cor = np.abs(v) 
            curr_cor = np.abs(correct_temperature(curr, temp)) 
        elif (fInvert and not fCorrect):
            v_cor = np.abs(v) 
            curr_cor = np.abs(curr)
        elif (not fInvert and fCorrect):
            v_cor = v
            curr_cor = correct_temperature(curr, temp)
        else:
            v_cor = v
            curr_cor = curr
        
        out.append([v_cor, ch, curr_cor, curr_err, tot_curr, v_msr, curr, temp, hum])
    
    return np.array(out)
 
 
def save_file(fn, fn2, dat, hd, fInvert, fCorrect):
    hd += '# Inverted: \t\t\t%d\n' % fInvert + '# Temperature Corrected: \t%d\n' % fCorrect \
        + '# Voltage [V] | Channel [-] | Current [nA] | Error [nA] | Tot. curr. [nA] | Act. vlt. [V] | Orig. curr. [nA] | Temp [C] | Hum. [%]\n' 
    if fn2 == "default":
        np.savetxt(fn[:-4] + '_corrected.txt', dat, fmt='%d\t %4d\t%10.3E\t%10.3E\t%10.3E\t%10.2E\t%10.3E\t%.1f\t%.1f', delimiter='\t', newline='\n', header=hd)
    else:
        np.savetxt(fn2, dat, fmt='%d\t %4d\t%10.3E\t%10.3E\t%10.3E\t%10.2E\t%10.3E\t%.1f\t%.1f', delimiter='\t', newline='\n', header=hd)
    return 0
    


## Main Executable
def main():
    usage = "usage: ./correct.py -i input_path [options]"
    
    parser = OptionParser(usage=usage, version="prog 0.1")
    parser.add_option("-i", "--input", action="store", dest="input", type="string", help="input file")
    parser.add_option("-o", "--output", action="store", dest="output", type="string", default="default",  help="output file")
    parser.add_option("--inv", "--invert", action="store", dest="fInvert", type="int", default=0,  help="flag to invert voltages and currents")
    parser.add_option("--cor", "--correct", action="store", dest="fCorrect", type="int", default=1,  help="flag to correct currents to 20 degree C")  
    parser.add_option("--ex", "--examples", action="store_true", dest="fExamples",  help="print examples") 
    
    (options, args) = parser.parse_args()
    
    if options.fExamples:
        print '\nSome example commands for running this script\n'
        print ''' ./correct_iv.py -i HPK_6in_135_4002_IV.txt --cor 1 --inv 1\t\tRead data file, correct temperature and invert voltages/currents'''
        print ''' ./correct_iv.py -i HPK_6in_135_4002_IV.txt --cor 1 --inv 0\t\tRead data file, correct temperature and but leave voltages/currents as is'''
        print ''' ./correct_iv.py -i HPK_6in_135_4002_IV.txt --cor 0 --inv 1\t\tRead data file, invert voltages/currents but dont correct anything'''
        print ''' ./correct_iv.py -i HPK_6in_135_4002_IV.txt --cor 0 --inv 0\t\tRead data file and create a copy with name 'HPK_6in_135_4002_IV_corrected.txt' '''
        print ''' ./correct_iv.py -i HPK_6in_135_4002_IV.txt -o output.txt --cor 0 --inv 0\t\tRead data file and create a copy with name 'output.txt' '''
        

    else:
        hd = read_header(options.input)
        dat = read_file(options.input)
        out = process_file(dat, options.fInvert, options.fCorrect)
        ret = save_file(options.input, options.output, out, hd, options.fInvert, options.fCorrect)
    

if __name__ == "__main__":
    main()





