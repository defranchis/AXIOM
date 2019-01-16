import logging
import numpy as np


# Math Tools
# -----------------------------------

def lcr_series_equ(f, z, phi):
    """
    Returns the series equivalent values.
    
    f    ... frequency in [Hz]
    z     ... magnitude of impedance in [Ohm]
    phi ... phaseshift in [rad]
    """
    
    r_s = z * np.cos(phi)
    x_s = z * np.sin(phi)
    c_s = -1 / (2 * np.pi * f * x_s)
    l_s = x_s / (2 * np.pi * f)
    D = r_s/x_s
    
    return r_s, c_s, l_s, D


def lcr_parallel_equ(f, z, phi):
    """
    Returns the parallel equivalent values.

    f    ... frequency in [Hz]
    z     ... magnitude of impedance in [Ohm]
    phi ... phaseshift in [rad]
    """

    y = 1/z
    g_p = y * np.cos(phi)
    b_p = y * np.sin(phi)
    r_p = 1/g_p
    c_p = -b_p / (2 * np.pi * f)
    l_p = 1 / (2 * np.pi * f * b_p)  * (-1)
    D = g_p/b_p

    return r_p, c_p, l_p, D


def lcr_open_cor(c_x, c_open):
    """
    Returns the open corrected DUT impedance z_dut.

    c_x     ... measured DUT impedance
    c_open     ... measured open impedance
    """

    return c_x - c_open


def lcr_open_short_cor(z_x, z_open, z_short):
    """
    Returns the open and short corrected DUT impedance z_dut.

    z_x     ... measured DUT impedance
    z_open     ... measured open impedance
    z_short ... measured short impedance
    """

    return (z_x-z_short) / (1 - (z_x-z_short) * (1/z_open))


def lcr_open_short_load_cor(z_x, z_open, z_short, z_load, z_std):
    """
    Returns the open, short and load corrected DUT impedance z_dut.

    Z_x     ... measured DUT impedance
    z_open     ... measured open impedance
    z_short ... measured short impedance
    z_load     ... measured impedance of the load device
    z_std   ... true value of the load device
    """

    return z_std * ((z_short-z_x) * (z_load-z_open)) / ((z_x-z_open) * (z_short-z_load))



def lcr_error_cp(f, z, z_err, phi, phi_err):
    """
    Returns the error on parallel equivalent capacitance.

    f        ... frequency in [Hz]
    z         ... magnitude of impedance in [Ohm]
    z_err   ... impedance error  in [Ohm]
    phi     ... phaseshift in [rad]
    phi_err ... phaseshift error in [rad]
    """

    y = 1/z
    b_p = y * np.sin(phi)
    c_p = -b_p / (2 * np.pi * f)

    y_err = z_err / z**2
    bp_err = np.sqrt( (y_err * np.sin(phi))**2 + (phi_err * y * np.cos(phi))**2 )
    cp_err = bp_err / (2 * np.pi * f)

    return cp_err


def lcr_error_cs(f, z, z_err, phi, phi_err):
    """
    Returns the error on series equivalent capacitance.

    f        ... frequency in [Hz]
    z         ... magnitude of impedance in [Ohm]
    z_err   ... impedance error in [Ohm]
    phi     ... phaseshift in [rad]
    phi_err ... phaseshift error in [rad]
    """

    xs_err = np.sqrt( (z_err*np.sin(phi))**2 + (phi_err*np.cos(phi))**2 )
    c_s = xs_err / (2 * np.pi * f * x_s**2)

    return cs_err



def extract_depletion_voltage(volts, caps, caps_err, v1_low, v1_up, v2_low, v2_up):
    """
    Returns depletion voltage in [V] from CV curve.

    volts    ... volts in [V]
    caps     ... capacitance in [F]
    caps_err ... capacitance error in [F]
    v1_low   ... lower fit range for first fit in [V]
    v1_up    ... upper fit range for first fit in [V]
    v2_low   ... lower fit range for second fit in [V]
    v2_up    ... upper fit range for second fit in [V]
    """

    x = volts
    y = 1 / caps**2
    y_err = 2*caps_err / caps**3

    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for i in range(len(x)):
        if (x[i] >= v1_low and x[i] <= v1_up):
            x1.append(x[i])
            y1.append(y[i])
        if (x[i] >= v2_low and x[i] <= v2_up):
            x2.append(x[i])
            y2.append(y[i])

    r1 = np.polyfit(x1, y1, 1)
    r2 = np.polyfit(x2, y2, 1)

    vdep = (r2[1] - r1[1]) / (r1[0] - r2[0])

    return vdep


def calculate_active_thickness(cap, area):
    """
    Returns active thickness in [cm] from capacitance value.

    area    ... implant size in [cm^2]
    cap     ... capacitance in [F]
    """

    e0 = 8.854187817 * 10**(-12)
    er = 11.68

    wdep = e0 * er * area / cap 

    return wdep * 10**(-2)


def extract_resistivity(volts, caps, caps_err, v1_low, v1_up, v2_low, v2_up, carrier, area):
    """
    Returns depletion voltage in [V], resistivity in [Ohm*cm] and doping concentration in [cm-3] from CV curve.

    volts    ... volts in [V]
    caps     ... capacitance in [F]
    caps_err ... capacitance error in [F]
    v1_low   ... lower fit range for first fit in [V]
    v1_up    ... upper fit range for first fit in [V]
    v2_low   ... lower fit range for second fit in [V]
    v2_up    ... upper fit range for second fit in [V]
    carrier  ... electrons or holes
    area     ... implant size in [cm^2]
    """

    x = volts
    y = 1 / caps**2
    y_err = 2*caps_err / caps**3

    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for i in range(len(x)):
        if (x[i] >= v1_low and x[i] <= v1_up):
            x1.append(x[i])
            y1.append(y[i])
        if (x[i] >= v2_low and x[i] <= v2_up):
            x2.append(x[i])
            y2.append(y[i])

    r1 = np.polyfit(x1, y1, 1)
    r2 = np.polyfit(x2, y2, 1)

    if carrier == 'holes':
        mu = 450 # cm^2/Vs
    elif carrier == 'electrons':
        mu = 1350 # cm^2/Vs
    else:
        raise ValueError('Not a valid type of majority carrier.')

    #mu *= 10**(-4)
    q = 1.60217662 * 10**(-19)
    e0 = 8.854187817 * 10**(-12)
    er = 11.68

    vdep = (r2[1] - r1[1]) / (r1[0] - r2[0]) # V
    conc = 2/(q * e0 * er * 10**(-2) * r1[0] * area**2)
    res = 1 / (mu * q * conc)

    return vdep, res, conc




# Misc Tools
# -----------------------------------

def add_coloring_to_emit_windows(fn):
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE      = 0x0001 # text color contains blue.
        FOREGROUND_GREEN     = 0x0002 # text color contains green.
        FOREGROUND_RED       = 0x0004 # text color contains red.
        FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
        FOREGROUND_WHITE     = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED
        
        # winbase.h
        STD_INPUT_HANDLE     = -10
        STD_OUTPUT_HANDLE    = -11
        STD_ERROR_HANDLE     = -12

        # wincon.h
        FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE      = 0x0001
        FOREGROUND_GREEN     = 0x0002
        FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED       = 0x0004
        FOREGROUND_MAGENTA   = 0x0005
        FOREGROUND_YELLOW    = 0x0006
        FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

        BACKGROUND_BLACK     = 0x0000
        BACKGROUND_BLUE      = 0x082567
        BACKGROUND_GREEN     = 0x0020
        BACKGROUND_CYAN      = 0x0030
        BACKGROUND_RED       = 0x0040
        BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW    = 0x0060
        BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080 # background color is intensified.     

        levelno = args[1].levelno
        if(levelno >= 50):
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY 
        elif(levelno >= 40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno >= 30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno >= 20):
            color = BACKGROUND_BLUE | FOREGROUND_WHITE
        elif(levelno >= 10):
            color = FOREGROUND_MAGENTA
        else:
            color = BACKGROUND_BLUE | FOREGROUND_WHITE
        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color( FOREGROUND_WHITE )

        return ret

    return new



def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        
        if(levelno >= 50):
            color = '\x1b[31m' # red
        elif(levelno >= 40):
            color = '\x1b[31m' # red
        elif(levelno >= 30):
            color = '\x1b[33m' # yellow
        elif(levelno >= 20):
            color = '\x1b[0m' # green 
        elif(levelno >= 10):
            color = '\x1b[35m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].msg = color + args[1].msg +  '\x1b[0m' 

        return fn(*args)
    
    return new