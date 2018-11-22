from subprocess import check_output, check_call, Popen
from os import path

def write_log_entry(context, msg):
    Log = context.klass("android.util.Log")
    Log.i("IntentFuzzer", msg)
    
def logcat_listen(context, filePath, androidSDK):    
    check_call([androidSDK + "platform-tools/adb", "logcat", "-c"])
    with open(filePath, "w") as f:
        f.flush()
        return Popen([androidSDK + "platform-tools/adb", "logcat"], stdout=f)
    
