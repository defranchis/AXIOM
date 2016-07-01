# ============================================================================
# File: hp4284A.py
# -----------------------
# Communication for Keysight HP4284A lcr meter.
# 
# Date: 12.06.2016
# Author: Florian Pitters
#
# ============================================================================

from pyvisa_device import device, device_error


class hp4284A(device):
    print 'hello'