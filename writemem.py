import lldb
import re
from StringIO import *

hit_loc = []
def get_ASLR():
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('image list -o', returnObject)
    output = returnObject.GetOutput();
    match = re.match(r'.+(0x[0-9a-fA-F]+)', output)
    if match:
        return match.group(1)
    else:
        return None

def br_callBack(frame, bp_loc, dict):
    br_id = bp_loc.GetBreakpoint().GetID()
    print "[-] br %d hitted in 0x%x" % (br_id,bp_loc.GetAddress())
    hit_loc.append(bp_loc.GetAddress().GetFileAddress())
    target = lldb.debugger.GetSelectedTarget()
    target.BreakpointDelete(br_id)
    response = lldb.SBCommandReturnObject()
    interpreter = lldb.debugger.GetCommandInterpreter()
    interpreter.HandleCommand("c",response)
    
def getALLdisabledBr(debugger, command, result, internal_dict):
    
    response = lldb.SBCommandReturnObject()
    interpreter = lldb.debugger.GetCommandInterpreter()
    interpreter.HandleCommand("br l",response)
    if response.Succeeded():
        output = response.GetOutput()
        #print output
        if output:
            f = StringIO(output)
            for l in f.readlines():
                match = re.match(r'.*\[(0x[0-9a-f]*)\]',l)
                if match:
                    print match.group(1)

def getALLHitedBr(debugger, command, result, internal_dict):
    with open(PATH_OF_HITTED_BR,"w+") as f:
        for h in hit_loc:
            print "0x%x" % h
            f.write(hex(h).rstrip('L')+'\n')



def getAlllocation(debugger, command, result, internal_dict):
    response = lldb.SBCommandReturnObject()
    interpreter = lldb.debugger.GetCommandInterpreter()
    interpreter.HandleCommand("di",response)
    if response.Succeeded():
                output = response.GetOutput()
                loc_list = []
                if output:
                    f = StringIO(output)
                    for l in f.readlines():
                        #print l
                        match = re.match(r'.*(0x[0-9a-f]*) <',l)
                        if match:
                            print match.group(1)
                            loc_list.append(match.group(1).strip())
                    return loc_list

def setBlock(debugger, command, result, internal_dict):
    aslr = get_ASLR()
    target = debugger.GetSelectedTarget()
    
    with open(PATH_OF_BLOCKADDR,'r+') as f:
        for l in f.readlines():
            if l:
                print "br at 0x%x"  % (eval(l)+eval(aslr))
                br = target.BreakpointCreateByAddress(eval(l)+eval(aslr))
                br.SetScriptCallbackFunction("setAllbr.br_callBack")



def writemem(debugger, command, result, internal_dict):
    
    
    new_value = "/usr/lib/dyld"
    error = lldb.SBError()
    process = lldb.debugger.GetSelectedTarget().GetProcess()
    result = process.WriteMemory(0x0011000c, new_value, error)
    if not error.Success() or result != len(new_value):
        print 'SBProcess.WriteMemory() failed!'
        



def get_frame():
    """
    Get the current frame and return it to the calling function
    """
    ret = None

    for t in lldb.debugger.GetSelectedTarget().process:
        if t.GetStopReason() != lldb.eStopReasonNone and t.GetStopReason() != lldb.eStopReasonInvalid:
            ret = t.GetFrameAtIndex(0)
    return ret


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f writemem.writemem writemem")


