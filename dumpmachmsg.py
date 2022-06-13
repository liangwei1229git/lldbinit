import lldb
import struct
import os
import sys


# Servername= sys.argv[1]#'com.apple.windowserver.active'

HookedMsg=[]
class Mach_msg:
	def __init__(self,machmsg):

		self.mach_bits = struct.unpack('<i',machmsg[0x0:0x4])[0]
		self.mach_size = struct.unpack('<i',machmsg[0x4:0x8])[0]
		self.mach_localport = struct.unpack('<i',machmsg[0x8:0xc])[0]
		self.mach_remoteport = struct.unpack('<i',machmsg[0xc:0x10])[0]
		self.mach_voucher = struct.unpack('<i',machmsg[0x10:0x14])[0]
		self.mach_id = struct.unpack('<i',machmsg[0x14:0x18])[0]
		self.DescriptionCount = 0
		if self.isComplexMsg():
			#complex msg
			self.DescriptionCount = struct.unpack('<i',machmsg[0x18:0x1c])[0]

	def isComplexMsg(self):
		return self.mach_bits < 0

	def printInfo(self):
		print(hex(self.mach_bits))
		print(hex(self.mach_size))
		print(hex(self.mach_localport))
		print(hex(self.mach_remoteport))
		print(hex(self.mach_voucher))
		print(hex(self.mach_id))
		if self.isComplexMsg():
			print('it s complex msg')
			print(hex(self.DescriptionCount))

def saveToFile(filename,content):
	with open(filename,'wb+') as f:
		f.write(content)

def getFirstArg(debugger, command, result, internal_dict):
	interpreter = debugger.GetCommandInterpreter()
	returnObject = lldb.SBCommandReturnObject()
	interpreter.HandleCommand('po $rdi', returnObject)
	x0 = returnObject.GetOutput()
	return int(x0)

def getMachMsgSize(debugger,addr):
	error = lldb.SBError()
	process = lldb.debugger.GetSelectedTarget().GetProcess()
	mach_size = process.ReadMemory(addr+4,4,error)
	mach_size = struct.unpack('<i',mach_size)[0]
	return mach_size

def getMachMsgID(debugger,addr):
	error = lldb.SBError()
	process = lldb.debugger.GetSelectedTarget().GetProcess()
	mach_id = process.ReadMemory(addr+0x14,4,error)
	mach_id = struct.unpack('<i',mach_id)[0]
	return str(mach_id)

def dumpmachmsg(debugger, command, result, internal_dict):
	ROOT_PATH= command
	
	process = debugger.GetSelectedTarget().GetProcess()
	error = lldb.SBError()

	mach_msg_addr =  getFirstArg(debugger, command, result, internal_dict)
	mach_size = getMachMsgSize(debugger,mach_msg_addr)
	# print("msg_size: %d" % mach_size)
	machmsg = process.ReadMemory(mach_msg_addr,mach_size,error)


	m = Mach_msg(machmsg)
	# m.printInfo()
	if (HookedMsg.count(m.mach_id) > 1):
		return

	HookedMsg.append(m.mach_id)
	#dump all mach msg to file
	if not os.path.exists(ROOT_PATH):
		os.mkdir(ROOT_PATH)
	filename = os.path.join(ROOT_PATH,str(m.mach_id))
	saveToFile(filename,machmsg)

	#if complex 
	#parse complex message
	if m.isComplexMsg():
		cursor = 0x1c
		for i in range(0,m.DescriptionCount):
			descriptionType = struct.unpack('<b',machmsg[cursor+0xb:cursor+0xc])[0]
			if descriptionType == 0: #port
				filename = str(m.mach_id) +'_port_'+'%d' % i
				filename = os.path.join(ROOT_PATH,filename)
				saveToFile(filename,'')
				cursor = cursor+0xc
			elif descriptionType == 1: #ool
				ool_address = struct.unpack('<q',machmsg[cursor:cursor+0x8])[0]
				ool_size = struct.unpack('<i',machmsg[cursor+0xc:cursor+0x10])[0]
				if ool_size >0:
					ool_content = process.ReadMemory(ool_address,ool_size,error)
				else:
					ool_content = ''
				filename = str(m.mach_id) +'_oolAddress_'+'%d' % i
				filename = os.path.join(ROOT_PATH,filename)
				saveToFile(filename,ool_content)
				cursor = cursor+0x10






def __lldb_init_module(debugger, internal_dict):

    debugger.HandleCommand("command script add -f dumpmachmsg.dumpmachmsg dumpmachmsg")
    print("Usage:  dumpmachmsg [Path_to_Save_machmsg]")
