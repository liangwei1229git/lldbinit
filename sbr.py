import lldb
import commands
import optparse
import shlex
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
        if match:
            return match.group(1)
        else:
            return None



# Super breakpoint
def sbr(debugger, command, result, internal_dict):
    commandArray = command.split(" ")
    if len(commandArray) == 1:
        if not command:
            print >>result, 'Please input the address!'
            return
        ASLR = get_ASLR()
        if ASLR:
            debugger.HandleCommand('br set -a "%s+%s"' % (ASLR, command))
        else:
            print >>result, 'ASLR not found!'
    elif  len(commandArray) == 2:
        print "set break point at 0x%x of %s" %(eval(commandArray[1]),commandArray[0])
        ASLR = get_ASLR(commandArray[0])
        if ASLR:
            debugger.HandleCommand('br set -a "%s+%s"' % (ASLR, commandArray[1]))
        else:
            print >>result, 'ASLR not found!'
            

# And the initialization code to add your commands 
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add sbr -f sbr.sbr')
    print 'The "sbr" python command has been installed and is ready for use.'
