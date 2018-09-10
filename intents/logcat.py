from subprocess import check_output, check_call, CalledProcessError

def write_log_entry(context, msg):
    Log = context.klass("android.util.Log")
    Log.i("IntentFuzzer", msg)
    
def flush_logcat(context, androidSDK):
    try:
        check_call([androidSDK + "platform-tools/adb", "logcat", "-b", "main", "-b", "crash", "-c"])
    except CalledProcessError as e:
        context.stderr.write("Failed calling logcat: %s\n" % e.output)

def dump_logcat(context, androidSDK, filePath):
    try:
        output = check_output([androidSDK + "platform-tools/adb", "logcat", "-b", "main", "-b", "crash", "-v", "tag", "-d"])
        with open(filePath, 'w') as file:
            file.write(output)
    except CalledProcessError as e1:
        context.stderr.write("Failed calling logcat: %s\n" % e1.output)
    except IOError as e2:
        context.stderr.write("Failed saving logcat output: I/O error (%s): %s\n" % (e2.errno, e2.strerror))
    return None
    
