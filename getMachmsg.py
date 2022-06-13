import lldb

def getMachmsg(debugger, command, result, internal_dict):
    
 	interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('x/10x $rdi', returnObject)
    output = returnObject.GetOutput();
    



def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f getMachmsg.getMachmsg getmachmsg")