#!/usr/bin/python
import os
import sys
import numpy as np
from cmath import *
from optparse import OptionParser

# Constants
kBoltzmann = 8.61733 * 10**(-5)  # [ev/K]
kZero = 273.15  # K


# Definitions
def lcr_open_cor(z_x, z_open):
    return 1/(1/z_x - 1/z_open)


def lcr_open_short_cor(z_x, z_open, z_short):
    return (z_x - z_short) / (1 - (z_x - z_short) * (1 / z_open))


def lcr_open_short_load_cor(z_m, z_open, z_short, z_load, z_std):
    return z_std * ((z_short - z_m) * (z_load - z_open)) / ((z_m - z_open) *
                                                            (z_short - z_load))


def lcr_parallel_equ(f, z, phi):
    y = 1 / z
    g_p = y * np.cos(phi)
    b_p = y * np.sin(phi)
    r_p = 1 / g_p
    c_p = -b_p / (2 * np.pi * f)
    l_p = 1 / (2 * np.pi * f * b_p) * (-1)
    D = g_p / b_p

    return r_p, c_p, l_p, D


def lcr_series_equ(f, z, phi):
    r_s = z * np.cos(phi)
    x_s = z * np.sin(phi)
    c_s = -1 / (2 * np.pi * f * x_s)
    l_s = x_s / (2 * np.pi * f)
    D = r_s / x_s

    return r_s, c_s, l_s, D


def lcr_error_cp(f, z, z_err, phi, phi_err):
    y = 1 / z
    b_p = y * np.sin(phi)
    c_p = -b_p / (2 * np.pi * f)
    y_err = z_err / z**2
    bp_err = np.sqrt((y_err * np.sin(phi))**2 + (phi_err * y * np.cos(phi))**2)
    cp_err = bp_err / (2 * np.pi * f)

    return cp_err


def lcr_error_cs(f, z, z_err, phi, phi_err):
    x_s = z * np.sin(phi)
    xs_err = np.sqrt((z_err * np.sin(phi))**2 + (phi_err * np.cos(phi))**2)
    cs_err = xs_err / (2 * np.pi * f * x_s**2)

    return cs_err


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


def find_correction_file(fn, open_file, short_file):

    # if files are provided, use them
    if (open_file != "" and short_file != ""):
        fOpen = open_file
        fShort = short_file

    # else look for default paths
    else:
        fOpen = ''
        fShort = ''

        if os.name == 'nt':
            m = '\\'
            sp = fn.split(m)
            ln = len(sp)
        else:
            m = '/'
            sp = fn.split(m)
            ln = len(sp)

        if (ln == 1):
            print "Something went wrong. Can't find correction files."
            sys.exit()
        else:
            path = ''
            typ = ''
            wp = sp[-1].split('_')
            for s in sp[:-2]:
                path += s + m
            for w in wp[:-2]:
                typ += w + '_'
            typ = typ[:-1]
            num = wp[-2]
            name = typ + '_' + num

        # Top folder
        # fOpen += '%s' % path + typ + '_Correction_Open' + m + typ + '_Open_CV.txt'
        # fShort += '%s' % path + typ + '_Correction_Short' + m + typ + '_Short_CV.txt'

        # Same folder
        fOpen += '%s' % path + name + m + typ + '_Open_CV.txt'
        fShort += '%s' % path + name + m + typ + '_Short_CV.txt'

    try:
        tmp = np.loadtxt(fOpen, dtype='float', comments='#')
        tmp = np.loadtxt(fShort, dtype='float', comments='#')
        print "Using corrections from:\n"
        print fOpen
        print fShort
    except:
        print "Something went wrong. Can't find correction files."
        sys.exit()

    return fOpen, fShort


def process_file(dat, fOpen, fShort, freq, fInvert, fCor):
    dat_open = read_file(fOpen)
    dat_short = read_file(fShort)

    volts = []
    for line in dat:
        v = line[0]
        if v in volts:
            pass
        else:
            volts.append(v)

    out = []
    for volt in volts:
        tmp_msr = np.array([val for val in dat if (val[0] == volt)])
        tmp_open = np.array([val for val in dat_open if (val[0] == volt)])

        if (len(tmp_open) > 1 and len(tmp_msr) > 1):

            for line in tmp_msr:
                v = line[0]
                ch = line[1]
                v_msr = line[5]
                temp = line[7]
                hum = line[8]
                r = line[11]
                r_err = line[12]
                phi = line[13]
                phi_err = line[14]
                tot_curr = line[4]

                if (r == 0):
					r = np.nan

                if (fInvert):
                    v_cor = np.abs(v)
                else:
                    v_cor = v

                z = rect(r, phi)
                cp = lcr_parallel_equ(freq, abs(z), phase(z))[1] * 10**12
                cs = lcr_series_equ(freq, abs(z), phase(z))[1] * 10**12

                r_open = np.array([val for val in tmp_open if (val[1] == ch)])[0, 11]
                phi_open = np.array([val for val in tmp_open if (val[1] == ch)])[0, 13]
                z_open = rect(r_open, phi_open)
                
                z_ocor = lcr_open_cor(z, z_open)
                cp_ocor = lcr_parallel_equ(freq, abs(z_ocor), phase(z_ocor))[1] * 10**12
                cs_ocor = lcr_series_equ(freq, abs(z_ocor), phase(z_ocor))[1] * 10**12
                cp_ocor_err = lcr_error_cp(freq, r, r_err, phi, phi_err) * 10**12
                
                r_short = np.array(
                    [val for val in dat_short if (val[1] == ch)])[0, 11]
                phi_short = np.array(
                    [val for val in dat_short if (val[1] == ch)])[0, 13]
                z_short = rect(r_short, phi_short)

                z_scor = lcr_open_short_cor(z, z_open, z_short)
                cp_scor = lcr_parallel_equ(freq, abs(z_scor), phase(z_scor))[1] * 10**12
                cp_scor_err = lcr_error_cp(freq, r, r_err, phi, phi_err) * 10**12

                if (1): # ocor
                    out.append([v_cor, ch, cp_ocor, cp_ocor_err, tot_curr, v_msr, cp, temp, hum, abs(z_ocor), phase(z_ocor),
                            abs(z), phase(z), abs(z_open), phase(z_open), abs(z_short), phase(z_short)])
                else: # scor
                    out.append([v_cor, ch, cp_scor, cp_scor_err, tot_curr, v_msr, cp, temp, hum, abs(z_scor), phase(z_scor),
                            abs(z), phase(z), abs(z_open), phase(z_open), abs(z_short), phase(z_short)])
                        
    return np.array(out)


def save_file(fn, fn2, dat, hd, fInvert, fCorrect):
    hd += '# Inverted: \t\t\t%d\n' % fInvert + '# Temperature Corrected: \t%d\n' % fCorrect \
        + '# Voltage [V] | Channel [-] | Cp [pF] | Error [pF] | Tot. curr. [nA] | Act. vlt. [V] | Orig. Cp [pF] | Temp [C] | Hum. [%]' \
        + '# Z_cor [Ohm] | Phi_cor [Ohm] | Z_orig [Ohm] | Phi_orig [Ohm] | Z_open [Ohm] | Phi_open [Ohm] |  Z_short [Ohm] | Phi_short [Ohm] |\n'
    if fn2 == "default":
        np.savetxt(
            fn[:-4] + '_corrected.txt',
            dat,
            fmt='%d\t %4d\t%8.5E\t%8.5E\t%8.3E\t%8.2f\t%8.5E\t%.1f\t%.1f\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E',
            delimiter='\t',
            newline='\n',
            header=hd)
    else:
        np.savetxt(
            fn2,
            dat,
            fmt='%d\t %4d\t%8.5E\t%8.5E\t%8.3E\t%8.2f\t%8.5E\t%.1f\t%.1f\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E\t%8.3E',
            delimiter='\t',
            newline='\n',
            header=hd)
    return 0


# Main Executable
def main():
    usage = "usage: ./correct.py -i input_path -o output_path"

    parser = OptionParser(usage=usage, version="prog 0.1")
    parser.add_option(
        "-i",
        "--input",
        action="store",
        dest="input",
        type="string",
        help="input file")
    parser.add_option(
        "-o",
        "--output",
        action="store",
        dest="output",
        type="string",
        default="default",
        help="output file")
    parser.add_option(
        "--inv",
        "--invert",
        action="store",
        dest="fInvert",
        type="int",
        default=0,
        help="flag to invert voltages")
    parser.add_option(
        "--cor",
        "--do_correction",
        action="store",
        dest="fCorrect",
        type="int",
        default=0,
        help="flag to do open-short correction")
    parser.add_option(
        "--freq",
        "--frequency",
        action="store",
        dest="freq",
        type="int",
        default=10000,
        help="frequency for the open-short correction")
    parser.add_option(
        "--ex",
        "--examples",
        action="store_true",
        dest="fExamples",
        help="print examples")
    parser.add_option(
        "--scf",
        "--short_correction_file",
        action="store",
        dest="short_file",
        type="string",
        default="",
        help="short correction file")
    parser.add_option(
        "--ocf",
        "--open_correction_file",
        action="store",
        dest="open_file",
        type="string",
        default="",
        help="open correction file")

    (options, args) = parser.parse_args()

    if options.fExamples:
        print '\nSome example commands for running this script\n'
        print ''' ./correct_cv.py -i HPK_6in_135_4002_CV.txt --cor 0 --inv 0 \t\tRead data file and create a copy with name '_corrected.txt'. '''
        print ''' ./correct_cv.py -i HPK_6in_135_4002_CV.txt --cor 1 --inv 1 --freq 50000 \t\tRead data file, invert voltages and correct capacitance. Use correction fiels from default location. '''

    else:
        hd = read_header(options.input)
        dat = read_file(options.input)
        fOpen, fShort = find_correction_file(options.input, options.open_file,
                                             options.short_file)
        out = process_file(dat, fOpen, fShort, options.freq, options.fInvert,
                           options.fCorrect)
        ret = save_file(options.input, options.output, out, hd,
                        options.fInvert, options.fCorrect)


if __name__ == "__main__":
    main()
