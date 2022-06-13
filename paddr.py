import lldb
import re
def get_ASLR(image):
    if not image:
        interpreter = lldb.debugger.GetCommandInterpreter()
        returnObject = lldb.SBCommandReturnObject()
        interpreter.HandleCommand('image list -o', returnObject)
        output = returnObject.GetOutput();
        match = re.match(r'.+(0x[0-9a-fA-F]+)', output)
        if match:
            return match.group(1)
        else:
            return None
    else:
        interpreter = lldb.debugger.GetCommandInterpreter()
        returnObject = lldb.SBCommandReturnObject()
        interpreter.HandleCommand('image list -o %s' % image, returnObject)
        output = returnObject.GetOutput();
        match = re.match(r'.+(0x[0-9a-fA-F]+)', output)
        print match
        if match:
            return match.group(1)
        else:
            return None


def paddr(debugger, command, result, internal_dict):
    aslr = 0
    cmdCount = len(command.split(" "))
    image=None
    address = 0
    if cmdCount == 2:
        image,address=command.split(" ")
    else:
        address = command
    if not image:
        aslr = get_ASLR(None)
    else:
        aslr = get_ASLR(command)
    print hex(int(address)+eval(aslr))

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f paddr.paddr paddr")