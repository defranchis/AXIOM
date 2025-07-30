# -----------------------------------------------------------------------------------------------------------
# These schemas are used to validate the configuration files
# Changing these is only required if you want to add verifications and will not infuence the code logic,  
#    (besides having to press yes to continue when the config doesn't match the schema.)
# -----------------------------------------------------------------------------------------------------------


BASE_SCHEMA = {
    'measurement_type': None,  # used to select which schema to validate, and which measurement class to execute
    'sample': {
        'type': None,           # only used for naming the files  / logs
        'id': None,             # only used for naming the files  / logs
        'preirradiated': None,  # used by gcdmos to determine some voltage logic
        'current_dose': None    # only used when no dose is communicated by the obelix control, for debugging purposes. 
    }
}

IRRADIATION_SCHEMA = {
    'doselist': None,   # List of doses
    'dose_rate': None,  # Float
    'voltage': None,    # Integer (in kV)
    'current': None,    # Integer (in mA)
    'biasing': None     # Boolean
}

ANNEALING_SCHEMA = {
    'period': None  # Integer (in minutes)
}

DIODE_IV_SCHEMA = {
    'devices': {
        'sourcemeter_1': {'model': None, 'address': None, 'lim_cur': None},
        'switch': {'model': None, 'address': None},
        'picoammeter_1': {'model': None, 'address': None},
        'picoammeter_2': {'model': None, 'address': None}
    },
    'measurements': {
        'IV': {
            'measurement_range': {'v_start': None, 'v_end': None, 'step_size': None},
            'bias_range': {'v_start': None, 'v_end': None, 'step_size': None},
            'delay': None,
            'sample_size': None
        }
    }
}

DIODE_CV_SCHEMA = {
    'devices': {
        'sourcemeter_1': {'model': None, 'address': None, 'lim_cur': None},
        'switch': {'model': None, 'address': None},
        'lcrmeter': {'model': None, 'address': None, 'mode': None, 'approx_open_corr': None}
    },
    'measurements': {
        'testset': None,
        'CV': {
            'range': {'v_start': None, 'v_end': None, 'step_size': None},
            'sample_size': None,
            'delay': None,
            'trig_delay': None,
            'lcr_amplitude': None,
            'lcr_frequency': None
        }
    }
}

GCDMOS_SCHEMA = {
    'devices': {
        'sourcemeter_1': {'model': None, 'address': None, 'lim_cur': None},
        'sourcemeter_2': {'model': None, 'address': None, 'lim_cur': None},
        'lcrmeter': {'model': None, 'address': None},
        'picoammeter': {'model': None, 'address': None, 'lim_cur': None}
    },
    'measurements': {
        'testset': None,
    }
}

STRIP_SCHEMA = {
    'devices': {
        'sourcemeter_1': {'model': None, 'address': None, 'lim_cur': None},
        'sourcemeter_2': {'model': None, 'address': None, 'lim_cur': None},
        'switch': {'model': None, 'address': None, 'connections': {'lcrmeter': None, 'picoammeter': None}},
        'lcrmeter': {'model': None, 'address': None},
        'picoammeter': {'model': None, 'address': None}
    },
    'measurements': {
        'CV': {
            'range': {'v_start': None, 'v_end': None, 'step_size': None},
            'sample_size': None,
            'lcr_amplitude': None,
            'frequencies': None,
            'delay': None
        },
        'IV': {
            'measurement_range': {'v_start': None, 'v_end': None, 'step_size': None},
            'bias_range': {'v_start': None, 'v_end': None, 'step_size': None},
            'sample_size': None,
            'delay': None,
            'step_delay': None
        }
    }
}
