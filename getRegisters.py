import lldb
PATH_OF_REGISTERS = '/Users/darthl/Desktop/idaresult/regiseters'
def getregisters(debugger, command, result, internal_dict):
	interpreter = debugger.GetCommandInterpreter()
        returnObject = lldb.SBCommandReturnObject()
        interpreter.HandleCommand('po $x0', returnObject)
        x0 = returnObject.GetOutput();
        print x0
        interpreter.HandleCommand('x/s $x1', returnObject)
        x1 = returnObject.GetOutput();
        interpreter.HandleCommand('po $x2', returnObject)
        x2 = returnObject.GetOutput();
        with open(PATH_OF_REGISTERS,'wb+') as f:
        	f.write(x0+'\n'+x1+'\n'+x2+'\n')


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f getRegisters.getregisters getregisters")