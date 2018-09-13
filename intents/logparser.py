import traceback
import json

def parse(appFilePath, crashFilePath, outputFilePath):
    try:
        (exceptions, exceptionsCount) = __parse_file(appFilePath)
        (tmp, crashCount) = __parse_file(crashFilePath)
        
        with open(outputFilePath, "w") as outputFile:
            result = {}
            result["numExceptions"] = exceptionsCount
            result["numCrashes"] = crashCount
            result["numIntents"] = len(exceptions)
            result["exceptions"] = exceptions
            json.dump(result, outputFile, indent=4)
            print("Tracked " + str(exceptionsCount) + " exceptions")
            print("Tracked " + str(crashCount) + " crashes")
    except:
        print("Failed parsing logfile: " + traceback.format_exc())
    

def __parse_file(inputFilePath):
    exceptionsCount = 0
    exceptions = {}
    stacktrace = None
    print("Parsing logfile: " + inputFilePath)
    with open(inputFilePath, "r") as inputFile:
        lastMessage = ""
        lastIntent = "UNKNOWN"
        for line in inputFile:
            line = line.strip()
            if line:
                tokens = line.split(":", 1)
                if len(tokens) > 1:
                    meta = tokens[0].strip()
                    message = tokens[1].strip()
                    if meta == "I/IntentFuzzer":
                        lastIntent = message
                    elif message.startswith("at "):
                        if not lastMessage.startswith("at "):
                            if not lastMessage.startswith("Caused by"):
                                if stacktrace is not None:
                                    exceptionsCount += 1
                                    __append_stacktarce(exceptions, stacktrace, lastIntent)
                                stacktrace = []
                            stacktrace.append(lastMessage)
                        stacktrace.append(message)
                    lastMessage = message
        exceptionsCount += 1
        __append_stacktarce(exceptions, stacktrace, lastIntent)
        return (exceptions, exceptionsCount)

def __append_stacktarce(exceptions, stacktrace, lastIntent):
    tmp = exceptions.get(lastIntent)
    if tmp == None:
        exceptions[lastIntent] = []
        exceptions[lastIntent].append(stacktrace)
    else:
        exceptions[lastIntent].append(stacktrace)
          
'''
def main():
  parse("/home/mark/deepthought/bachelor/AndroidApks/output/com.accuweather.android.app.log", 
        "/home/mark/deepthought/bachelor/AndroidApks/output/com.accuweather.android.crash.log",
        "/home/mark/deepthought/bachelor/AndroidApks/output/com.accuweather.android.json")
  
  
if __name__== "__main__":
  main()
'''
