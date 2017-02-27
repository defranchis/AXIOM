#!/usr/bin/python

import socket
import sys
import select
 
try:
	import gpib
except ImportError:
	print 'GPIB python-module not found'


def OpenGPIB(id):
	try:
		con= gpib.dev(0,id)
		command = '*IDN?'
		print command
		gpib.write(con,command)
		print gpib.read(con,1000)
		gpib.write(con,':OUTP:STAT ON')
		gpib.write(con,':ROUT:TERM REAR')
		gpib.write(con,':SOUR:VOLT:RANG MAX')
		return con
	except (NameError,gpib.GpibError):
		print 'Device not connected!'
		return -1

def SetVoltage(con, voltage):
	try:
		command = ':SOUR:VOLT:LEV:IMM:AMPL ' + str(voltage)
		#print command
		gpib.write(con,command)
	except (NameError,gpib.GpibError):
		return
	return

def SetCurrentLimit(con, limit):
	try:
		command = ':SENS:CURR:PROT:LEV ' + str(limit)
		print command
		gpib.write(con,command)
	except (NameError,gpib.GpibError):
		return
	return
	

def CheckCompliance(con):
	try:
	    command = ':SENS:CURR:PROT:TRIP?'
	    #print command
	    gpib.write(con,command)
	    res=gpib.read(con,1000)
	    return res
	except (NameError,gpib.GpibError):
		return 0
	return 0

def ReadCurrent(con):
	try:
		command = ':MEAS:CURR?'
		#print command
		gpib.write(con,command)
		res=gpib.read(con,1000)
		curr=res.split(',')
		print curr
		return curr[1]
	except (NameError,gpib.GpibError):
		return -1	

def ReadVoltage(con):
	try:
		command = ':MEAS:VOLT?'
		#print command
		gpib.write(con,command)
		res=gpib.read(con,1000)
		volt=res.split(',')
		print volt
		return volt[0]
	except (NameError,gpib.GpibError):
		return -1


def CloseGPIB(con):
	try:	
		SetVoltage(con,0)
		gpib.write(con,':OUTP:STAT OFF')
		gpib.close(con)
	except (NameError,gpib.GpibError):
		return
	return




def main():

	HOST = ''   # Symbolic name, meaning all available interfaces
	PORT = 8888 # Arbitrary non-privileged port
	 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#print 'Socket created'
	 
	#Bind socket to local host and port
	try:
	    s.bind((HOST, PORT))
	except socket.error as msg:
	    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	    sys.exit()
	     
	#print 'Socket bind complete'
	 
	#Start listening on socket
	s.listen(1)
	print 'Socket now listening'
	 
	#now keep talking with the client
	conn, addr = s.accept()
	#conn.setblocking(0)
	
	print 'Connected with ' + addr[0] + ':' + str(addr[1])

	gpibcon= {}

	while 1:

	    timeout_in_seconds = 2
	    ready = select.select([conn], [], [], timeout_in_seconds)
	    if ready[0]:
    		data = conn.recv(4096)
	    else:
	    #    print 'no command received, bias current: %d uA and %d uA' % ((ReadCurrent(gpibcon24)*1e6),(ReadCurrent(gpibcon25)*1e6))
			data=''

	    
	    command = data.split()

	    while len(command)>0:    	
			print command
			addr=0
			if (len(command[1])):
				addr=int(command[1])
		

				if (command[0]=='ConnectDevice'):
					print 'Connecting to Ke2410 on adress %d' % addr
					gpibcon[addr] = OpenGPIB(addr)
					print gpibcon
					command = command[2:]

				elif (command[0]=='SetVoltage'):
					try:
						print 'SetVoltage on channel %d to %f' % ((addr),float(command[2]))			    
						SetVoltage(gpibcon[addr],command[2])
						command = command[3:]
					except KeyError:
						print "No device at address %d connected!" % addr
				
				elif (command[0]=='ReadCurrent'):
					try:
						curr = ReadCurrent(gpibcon[addr])	
						conn.sendall(str(curr))    
						#print 'Bias current on channel %d is %d uA' % (int(command[1]),(curr*1e6))
						command = command[2:]
					except KeyError:
						print "No device at address %d connected!" % addr
				elif (command[0]=='ReadVoltage'):
					try:
						volt = ReadVoltage(gpibcon[addr])	
						conn.sendall(str(volt))    
						#print 'Bias voltage on channel %d is %d uA' % (int(command[1]),(volt*1e6))
						command = command[2:]
					except KeyError:
						print "No device at address %d connected!" % addr

				elif (command[0]=='SetCurrentLimit'):
					try:
						print 'Set current limit on channel %d to %f uA' % ((addr),float(command[2])*1e6)
						SetCurrentLimit(gpibcon[addr],command[2])
						command = command[3:]
					except KeyError:
						print "No device at address %d connected!" % addr
				
				elif (command[0]=='CheckCompliance'):
					try:
						comp=CheckCompliance(gpibcon[addr])
						conn.sendall(str(comp))
						command = command[2:]
					except KeyError:
						print "No device at address %d connected!" % addr

		 
			   	elif(command[0]=='exit'):
					for addr, con in gpibcon.iteritems():
						print 'Closing GPIB connection on address %d' % addr
						CloseGPIB(con)
					print 'Closing socket!' 
					s.close()
					return 0
			




if __name__ == "__main__":
    main()