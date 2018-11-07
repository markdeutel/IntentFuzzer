from subprocess import check_output, check_call, CalledProcessError, Popen

def write_log_entry(context, msg):
    Log = context.klass("android.util.Log")
    Log.i("IntentFuzzer", msg)
    
def logcat_listen(context, filePath, androidSDK):
    try:
        check_call([androidSDK + "platform-tools/adb", "connect", "192.168.189.39"])
        check_call([androidSDK + "platform-tools/adb", "logcat", "-c"])
        with open(filePath, "w") as f:
            f.flush()
            return Popen([androidSDK + "platform-tools/adb", "logcat"], stdout=f)
    except CalledProcessError as e:
        context.stderr.write("Failed calling logcat: %s\n" % str(e))
    
