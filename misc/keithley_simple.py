import visa

rm = visa.ResourceManager()
rm.list_resources()

keithley = rm.open_resource('GPIB0::24::INSTR')
print keithley.query('*IDN?')


## Resistance measurement
keithley.write("*RST")                  # Reset instrument to default parameters.
keithley.write(":SENS:FUNC 'RES' ")     # Select ohms measurement function.
keithley.write(":SENS:RES:NPLC 1")      # Set measurement speed to 1 PLC.
keithley.write(":SENS:RES:MODE MAN")    # Select manual ohms mode.
keithley.write(":SOUR:FUNC CURR")       # Select current source function.
keithley.write(":SOUR:CURR 0.01")       # Set source to output 10mA.
keithley.write(":SOUR:CLE:AUTO ON")     # Enable source auto output-off.
keithley.write(":SENS:VOLT:PROT 10")    # Set 10V compliance limit.
keithley.write(":TRIG:COUN 1")          # Set to perform one measurement.
keithley.write(":FORM:ELEM RES")        # Set to output ohms reading to PC.
print keithley.query(":READ?")          # Select ohms measurement function.
print keithley.query(":MEAS:RES?")         # Configure and read in the same call

print '#---------------'

## Current measurement
keithley.write("*RST")                      # Reset instrument to default parameters.
keithley.write(":SENS:FUNC 'CURR' ")        # Select ohms measurement function.
keithley.write(":SENS:CURR:NPLC 1")         # Set measurement speed to 1 PLC.
keithley.write(":SOUR:FUNC VOLT")           # Select voltage source function.
keithley.write(":SOUR:VOLT 10")             # Set voltage source to output 10V.
keithley.write(":SOUR:CLE:AUTO ON")         # Enable source auto output-off.
keithley.write(":SENS:CURR:PROT 0.00005")   # Set 50 uA compliance limit.
print keithley.query(':SENS:CURR:PROT:TRIP?') # Check if compliance is on
keithley.write(":TRIG:COUN 1")              # Set to perform one measurement.
keithley.write(":FORM:ELEM CURR")           # Read only current instead of (volt, current, resistance, x, x).
print keithley.query(":READ?")              # Execute the measurement
print keithley.query(":MEAS:CURR?")         # Configure and read in the same call

print '#---------------'

## Voltage Measurement
keithley.write("*RST")                      # Reset instrument to default parameters.
keithley.write(":SENS:FUNC 'VOLT' ")        # Select to measure voltage
keithley.write(":SENS:CURR:NPLC 1")         # Set measurement speed to 1 PLC.
keithley.write(":SOUR:FUNC CURR")           # Select current source function.
keithley.write(":SOUR:VOLT 0.01")           # Set current source to output 10mA.
keithley.write(":SOUR:CLE:AUTO ON")         # Enable source auto output-off.
keithley.write(":SENS:VOLT:PROT 10")        # Set 10V compliance limit.
keithley.write(":TRIG:COUN 1")              # Set to perform one measurement.
keithley.write(":FORM:ELEM VOLT")           # Set to output voltage reading to PC.
print keithley.query(":READ?")              # Read
print keithley.query(":MEAS:VOLT?")         # Configure and read in the same call


## General functions
# keithley.write(':OUTP:STAT ON')           # Set output on
# keithley.write(':ROUT:TERM REAR')
# keithley.write(':SOUR:VOLT:RANG MAX')     # Set all ranges to max
# keithley.write(':OUTP:STAT OFF')          # Set output off
# keithley.write(":SOUR:CLE:AUTO ON")       # Set auto on/off



print "Success!"







