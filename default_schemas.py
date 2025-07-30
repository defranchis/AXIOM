# schemas.py

BASE_SCHEMA = {
    'measurement_type': None,
    'sample': {
        'type': None,
        'id': None,
        'preirradiated': None,
        'current_dose': None
    }
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
        'sourcemeter_1': {'model': None, 'address': None, 'correction_count': None, 'lim_cur': None},
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
