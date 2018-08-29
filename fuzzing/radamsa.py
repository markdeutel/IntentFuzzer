from subprocess import Popen, PIPE, check_output, CalledProcessError

def next(type):
    if type == "integer" or type == "long" or type == "short":
        return next_int()
    elif type == "float" or type == "double":
        return next_float()
    elif type == "string":
        return next_string("hewhfbewfbw33f")
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
        return str(run_radamsa(str(source), ["-m", "num", "-n", str(count), "-p", "od"]).splitlines())
    
def next_string(source, count=1):
    assert count >= 1
    if count == 1:
        return str(run_radamsa(str(source)))
    else:
        output = []
        for x in xrange(count):
            output.append(str(run_radamsa(source)))
        return output

def run_radamsa(source, args=[]):
    try:
        ps = Popen(("echo", source), stdout=PIPE)
        output = check_output(["radamsa"] + args, stdin=ps.stdout)
    except CalledProcessError as e:
        output = e.output
    return output
