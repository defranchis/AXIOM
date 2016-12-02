import numpy as np


def lcr_series_equ(f, z, phi):
    r_s = z * np.cos(phi)
    x_s = z * np.sin(phi)
    c_s = 1 / (2 * np.pi * f * x_s)
    l_s = x_s / (2 * np.pi * f)
    D = r_s/x_s
    
    return r_s, c_s, l_s, D


def lcr_parallel_equ(f, z, phi):
    y = 1/z
    g_p = y * np.cos(phi)
    b_p = y * np.sin(phi)
    r_p = 1/g_p
    c_p = b_p / (2 * np.pi * f)
    l_p = 1 / (2 * np.pi * f * b_p)  * (-1)
    D = g_p/b_p 

    return r_p, c_p, l_p, D


def lcr_open_cor(c_x, c_open):
	"""
	Returns the open corrected DUT impedance z_dut.

	Z_x 	... measured DUT impedance
	z_open 	... measured open impedance
	z_s
	"""

	return c_x - c_open


def lcr_open_short_cor(z_x, z_open, z_short):
	"""
	Returns the open and short corrected DUT impedance z_dut.

	Z_x 	... measured DUT impedance
	z_open 	... measured open impedance
	z_short ... measured short impedance
	"""

	return (z_x-z_short) / (1 - (z_x-z_short) * (1/z_open))


def lcr_open_short_load_cor(z_x, z_open, z_short, z_load, z_std):
	"""
	Returns the open, short and load corrected DUT impedance z_dut.

	Z_x 	... measured DUT impedance
	z_open 	... measured open impedance
	z_short ... measured short impedance
	z_load 	... measured impedance of the load device 
	z_std   ... true value of the load device
	"""

	return z_std * ((z_short-z_x) * (z_load-z_open)) / ((z_x-z_open) * (z_short-z_load))





