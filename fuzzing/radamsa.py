from subprocess import Popen, PIPE, check_output, CalledProcessError
import random

def next(type):
    count = 1
    if "array" in type:
        count = random.randint(1, 100)
        
    if "integer" in type or "long" in type or "short" in type:
        return next_int(count)
    elif "float" in type or "double" in type:
        return next_float(count)
    elif "string" in type or "char" in type or "byte" in type:
        return next_string("hewhfbewfbw33f", count)
    return None

def next_int(count=1):
    return next_number(42, count)
    
def next_float(count=1):
    return next_number(0.42, count)
    
def next_number(source, count=1):
    assert count >= 1
    if count == 1:
        return str(run_radamsa(str(source), ["-m", "num", "-p", "od"]).strip())
    else:
        return str(run_radamsa(str(source), ["-m", "num", "-n", str(count), "-p", "od"]).replace("\n", " ").strip())
    
def next_string(source, count=1):
    assert count >= 1
    if count == 1:
        return str(run_radamsa(str(source)))
    else:
        output = ""
        for x in xrange(count):
            output += str(run_radamsa(source)) + " "
        return output.strip()

def run_radamsa(source, args=[]):
    try:
        ps = Popen(("echo", source), stdout=PIPE)
        output = check_output(["radamsa"] + args, stdin=ps.stdout)
    except CalledProcessError as e:
        output = e.output
    return output
