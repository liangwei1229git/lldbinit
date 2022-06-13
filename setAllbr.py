import lldb
import re
from StringIO import *
PATH_OF_BLOCKADDR = '/Users/darthl/Desktop/idaresult/blockaddr'
PATH_OF_HITTED_BR = '/Users/darthl/Desktop/idaresult/HittedBr'

hit_loc = []
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
    aslr = 0
    if  not command:
        aslr = get_ASLR(None)
    else:
        aslr = get_ASLR(command)
    target = debugger.GetSelectedTarget()
    with open(PATH_OF_BLOCKADDR,'r+') as f:
        for l in f.readlines():
            if l:
                print "br at 0x%x"  % (eval(l)+eval(aslr))
                br = target.BreakpointCreateByAddress(eval(l)+eval(aslr))
                br.SetScriptCallbackFunction("setAllbr.br_callBack")
        

        



def setAllbr(debugger, command, result, internal_dict):
    loc_list = getAlllocation(debugger, command, result, internal_dict)
    target = debugger.GetSelectedTarget()
    frame = get_frame()
    if frame:
        # Print some simple frame info
        print frame
        pcaddr = frame.GetPC()
        print "0x%x" % pcaddr
        for lo in loc_list:
            print "br at 0x%x of %s" % (eval(lo),command)
            br = target.BreakpointCreateByAddress(eval(lo))
            br.SetScriptCallbackFunction("setAllbr.br_callBack")
        



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
    debugger.HandleCommand("command script add -f setAllbr.setBlock setBlock")
    debugger.HandleCommand("command script add -f setAllbr.getAlllocation getAlllocation")
    debugger.HandleCommand("command script add -f setAllbr.getALLdisabledBr getALLdisabledBr")
    debugger.HandleCommand("command script add -f setAllbr.getALLHitedBr getALLHitedBr")

