import source_meter


class ke2450(source_meter):
    """ 
    Keithley 2450 source meter.
    
    Example:
    -------------
    dev = ke2450(address=24)
    dev.print_idn()
    dev.set_source('voltage')
    dev.set_voltage(10)
    dev.set_sense('current')
    dev.set_current_limit(0.00005)
    dev.set_output_on()
    print dev.read_current()
    print dev.read_voltage()
    print dev.read_resistance()
    dev.set_output_off()
    dev.reset()
    """



