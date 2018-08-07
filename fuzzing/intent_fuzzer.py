from drozer.modules import common, Module
from drozer import android

import json
import sys

class IntentTemplate:
    def __init__(self):
        self.packageName = ""
        self.componentName = ""
        self.extras = []
        
    def toString(self):
        extraStr = ""
        for extra in self.extras:
            extraStr += "returnType: " + extra[0] + " value: " + extra[1] + " "
        return "package: " + self.packageName + " component: " + self.componentName + " extra: " + extraStr;

class IntentFuzzer(Module, common.PackageManager):
    name = "fuzzinozer"
    description = "Android intent fuzzing module "
    examples = ""
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "2018-08-06"
    license = "3 clause BSD"
    path = ["fuzzing"]
    
    def add_arguments(self, parser):
        parser.add_argument("packageName")
    
    def execute(self, arguments):
        templates = self.buildIntentTemplates(arguments.packageName)
        for template in templates:
            self.stdout.write("%s\n" % template.toString())
                    
    def executeIntent(self, packageName, componentName):
        try:
            self.stdout.write("Sending intent: package: %s component: %s\n" % (packageName, componentName))
            intent = android.Intent(component = (packageName, componentName), flags = [])
            intent.flags.append("ACTIVITY_NEW_TASK")
            self.getContext().startActivity(intent.buildIn(self))
        except:
            self.stderr.write("Failed executing intent: %s\n" % sys.exc_info()[1])
            
    def buildIntentTemplates(self, packageName):
        intentTemplates = []
        datastore = self.getStaticAnalysisDatastore("/home/mark/deepthought/smali-analyser/output.json")
        packageInfo = self.packageManager().getPackageInfo(packageName, common.PackageManager.GET_ACTIVITIES)
        for component in packageInfo.activities:
            template = IntentTemplate()
            template.packageName = str(component.packageName)
            template.componentName = str(component.name)
            staticData = self.getStaticComponentData(datastore, component)
            if staticData != None:
                for invocation in staticData["invocations"]:
                    returnType = invocation["returnType"]
                    values = invocation["values"]
                    if(len(values) >= 1):
                        template.extras.append((returnType, values[0]))
            intentTemplates.append(template)
        return intentTemplates
            
    def getStaticAnalysisDatastore(self, source):
        try:
            with open(source, 'r') as file:
                return json.load(file)
        except:
            self.stderr.write("Failed reading static analysis data: %s\n" % sys.exc_info()[1])
            return None
            
    def getStaticComponentData(self, datastore, component):
        data = datastore.get(str(component.name))
        if data == None:
            data = datastore.get(str(component.targetActivity))
        return data
