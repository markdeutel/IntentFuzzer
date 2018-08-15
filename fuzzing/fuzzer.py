from drozer.modules import common, Module
from drozer.modules.common import loader
from drozer import android
from template import IntentTemplate

import json
import sys

class IntentFuzzer(Module, common.PackageManager, loader.ClassLoader):
    name = "Intent fuzzer"
    description = "Android intent fuzzing module"
    examples = ""
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "2018-08-10"
    license = "3 clause BSD"
    path = ["fuzzing"]
    
    staticSource = "/home/mark/deepthought/bachelor/output.json"
    
    def add_arguments(self, parser):
        parser.add_argument("packageName")
        parser.add_argument("numIter")
    
    def execute(self, arguments):
        templates = self.__build_intent_templates(arguments.packageName)
        for i in range(0, int(arguments.numIter)):
            for template in templates:
                self.__execute_intent(template)

    def __build_intent_templates(self, packageName):
        templates = []
        datastore = self.__get_static_datastore(IntentFuzzer.staticSource)
        packageInfo = self.packageManager().getPackageInfo(packageName, 
                                                           common.PackageManager.GET_ACTIVITIES |
                                                           common.PackageManager.GET_SERVICES |
                                                           common.PackageManager.GET_RECEIVERS)
        for activityInfo in packageInfo.activities:
            template = IntentTemplate(type="activity", component=(str(activityInfo.packageName), str(activityInfo.name)), extras=[], bundle=[])
            staticData = datastore.get(str(activityInfo.name))
            if staticData == None:
                staticData = datastore.get(str(activityInfo.targetActivity))
            if staticData != None:
                template.extras = self.__extract_invocations(staticData, "extras")
                template.bundle = self.__extract_invocations(staticData, "bundle")
            templates.append(template)
        for receiverInfo in packageInfo.receivers:
            template = IntentTemplate(type="broadcast", component=(str(receiverInfo.packageName), str(receiverInfo.name)), extras=[], bundle=[])
            staticData = datastore.get(str(receiverInfo.name))
            if staticData == None:
                staticData = datastore.get(str(receiverInfo.targetActivity))
            if staticData != None:
                template.extras = self.__extract_invocations(staticData, "extras")
                template.bundle = self.__extract_invocations(staticData, "bundle")
            templates.append(template)
        for serviceInfo in packageInfo.services:
            template = IntentTemplate(type="service", component=(str(serviceInfo.packageName), str(serviceInfo.name)), extras=[], bundle=[])
            staticData = datastore.get(str(serviceInfo.name))
            if staticData != None:
                template.extras = self.__extract_invocations(staticData, "extras")
                template.bundle = self.__extract_invocations(staticData, "bundle")
            templates.append(template)
        self.stdout.write("Created %i intent templates\n" % len(templates))
        return templates
    
    def __get_static_datastore(self, source):
        try:
            with open(source, 'r') as file:
                return json.load(file)
        except:
            self.stderr.write("Failed reading static analysis data: %s\n" % sys.exc_info()[1])
            return None
        
    def __extract_invocations(self, staticData, field):
        invocations = []
        for invocation in staticData[field]:
            returnType = invocation["returnType"]
            value = invocation["value"]
            invocations.append((returnType, value))
        return invocations
    
    def __execute_intent(self, template):
        try:
            if template.type == "activity":
                self.getContext().startActivity(template.buildIntent(self))
            elif template.type == "service":
                self.getContext().startService(template.buildIntent(self))
            elif template.type == "broadcast":
                self.getContext().sendBroadcast(template.buildIntent(self))
            else:
                self.stderr.write("Template has invalid type: expected 'activity', 'service' or 'broadcast', found %s" % template.type)
        except:
            self.stderr.write("Failed executing intent: %s\n" % sys.exc_info()[1])
