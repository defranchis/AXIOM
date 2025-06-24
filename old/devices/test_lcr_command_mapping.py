def TEST_set_mode(mode='CSRS', debug=0, **instructions):
    """
    Set the measurement mode for the Agilent 4263B.
    Compatible with legacy set_mode usage: lcr_meter.set_mode('RX')
    """
    if debug == 1:
        print("Setting measurement mode to %s. Options are ['RX', 'CSRS', 'CPRP', 'ZTD']." % mode)

    # this maps the (previously used) commands from the keysight E4980 to the agilent 4263b formatting
    # refer to E4980 manual: https://www.keysight.com/us/en/assets/9018-05655/user-manuals/9018-05655.pdf
    # and the 4263b  manual: https://www.keysight.com/us/en/assets/9018-01378/user-manuals/9018-01378.pdf
    MODE_MAP = {
        'RX': 'R-X',
        'CSRS': 'Cs-Rs',
        'CPRP': 'Cp-Rp',
        'ZTD': 'Z-thd'
    }
    if mode in MODE_MAP:
        lcr_measurement = MODE_MAP[mode]
    else:
        lcr_measurement = mode

    # Set the correct measurement mode and formatting for the Agilent 4263B
    # Again, check page 133 of https://www.keysight.com/us/en/assets/9018-01378/user-manuals/9018-01378.pdf
    VALID_prefix = {'Cp-D': 'FADM',
                    'R-X': 'FIMP',
                    'Cs-Rs': 'FIMP',
                    'Cp-Rp': 'FADM',
                    'Z-thd': 'FIMP',
                    'Cp-Q': 'FADM',
                    'Ls-Q': 'FIMP'}
    VALID_form = {'D': 'D',
                    'Cp': 'CP',
                    'Cs': 'CS',
                    'Ls': 'LS',
                    'Rs': 'REAL',
                    'Rp': 'RP',
                    'G': 'REAL',
                    'R': 'REAL',
                    'X': 'IMAG',
                    'Q': 'Q',
                    'Z': 'MLIN',
                    'thd' : 'PHAS',
                    }
    
    # Split the measurement info two parts for the relevant commands
    pivot = lcr_measurement.find("-")
    calc1 = lcr_measurement[:pivot]
    calc2 = lcr_measurement[pivot+1:]

    print(f":SENS:FUNC '" + VALID_prefix[lcr_measurement] + "'")
    print(f':CALC1:FORM {VALID_form[calc1]}')
    print(f':CALC2:FORM {VALID_form[calc2]}')


def main():
    test_modes = ['RX', 'CSRS', 'CPRP', 'ZTD', 'INVALID']
    for mode in test_modes:
        print(f"\nTesting mode: {mode}")
        try:
            TEST_set_mode(mode, debug=1)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()