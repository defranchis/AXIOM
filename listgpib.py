import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())

#rm.open_resource('GPIB0::%s::INSTR' % address)
