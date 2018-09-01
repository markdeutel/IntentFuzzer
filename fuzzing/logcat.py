from subprocess import check_output, check_call, CalledProcessError
from os import path

def write_log_entry(context, msg):
    Log = context.klass("android.util.Log")
    Log.i("FUZZER", msg)
    
def flush_logcat(context):
    try:
        check_call(["/home/mark/Android/Sdk/platform-tools/adb", "logcat", "-c"])
    except CalledProcessError as e:
        context.stderr.write("Failed calling logcat: %s\n" % e.output)

def dump_logcat(context, filePath):
    try:
        output = check_output(["/home/mark/Android/Sdk/platform-tools/adb", "logcat", "-d"])
        with open(path.expanduser(filePath), 'w') as file:
            file.write(output)
    except CalledProcessError as e1:
        context.stderr.write("Failed calling logcat: %s\n" % e1.output)
    except IOError as e2:
        context.stderr.write("Failed saving logcat output: I/O error (%s): %s\n" % (e2.errno, e2.strerror))
    return None
    
