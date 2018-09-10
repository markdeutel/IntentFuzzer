import sys
import json

def parse(inputFilePath, outputFilePath):
    try:
        exceptions = []
        stacktrace = None
        print("Parsing logfile: " + inputFilePath)
        with open(inputFilePath, "r") as inputFile:
            lastLine = ""
            for line in inputFile:
                line = line.strip()
                if line:
                    tokens = line.split(":", 1)
                    if len(tokens) > 1:
                        line = tokens[1].strip()
                        if line.startswith("at "):
                            if not lastLine.startswith("at "):
                                if not lastLine.startswith("Caused by"):
                                    if stacktrace is not None:
                                        exceptions.append(stacktrace)
                                    stacktrace = []
                                stacktrace.append(lastLine)
                            stacktrace.append(line)
                        lastLine = line
            exceptions.append(stacktrace)
        with open(outputFilePath, "w") as outputFile:
            result = {}
            result["exceptionsCount"] = len(exceptions)
            result["exceptions"] = exceptions
            json.dump(result, outputFile, indent=4)
            print("Found " + str(len(exceptions)) + " exceptions")
    except:
        print("Failed parsing logfile: " + sys.exc_info()[1])
          
def main():
  parse("/home/mark/deepthought/bachelor/AndroidApks/output/com.accuweather.android.log", 
            "/home/mark/deepthought/bachelor/AndroidApks/output/com.accuweather.android.log")
  
  
if __name__== "__main__":
  main()
