from drozer.modules import common, Module
from drozer.modules.common import loader

import json
import sys

class Fuzzer(Module, loader.ClassLoader):

    name = "Intent Fuzzer"
    description = "This module is used to generate fuzzed intents and send them."
    examples = ""
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "05.09.2018"
    license = "BSD (3-clause)"
    path = ["intents"]

    def add_arguments(self, parser):
        parser.add_argument("-p", "--packageName", help="specify the package which should be attacked.")
        parser.add_argument("-s", "--staticData", help="specify a path on your local machine to the static data file.")

    def execute(self, arguments):
        # build the intent templates
        templates = []
        dataStore = self.__load_data_store(arguments.staticData)
        packageManager = FuzzerPackageManager(self)
        for receiver in packageManager.get_receivers(arguments.packageName):
            templates.append(self.__build_template(dataStore, "receiver", (arguments.packageName, receiver)))
        for activity in packageManager.get_activities(arguments.packageName):
            templates.append(self.__build_template(dataStore, "activity", (arguments.packageName, activity)))
        for service in packageManager.get_services(arguments.packageName):
            templates.append(self.__build_template(dataStore, "service", (arguments.packageName, service)))
        # send all intent
        for template in templates:
            template.send(self)
    
    def __build_template(self, dataStore, type, component):
        staticData = json.dumps(dataStore.get(component[1], "{}"))
        return IntentTemplate(staticData, type, component)
    
    def __load_data_store(self, filePath):
        try:
            with open(filePath, 'r') as file:
                return json.load(file)
        except:
            self.stderr.write("Failed reading static analysis data: %s\n" % sys.exc_info()[1])
    
class IntentTemplate:
    
    def __init__(self, staticData, type, component):
        self.staticData = staticData
        self.component = component
        self.type = type
        
    def __build_intent(self, context):
        IntentBuilder = context.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__)
        return IntentBuilder.build(self.component[0], self.component[1], self.staticData)
        
    def send(self, context):
        try:
            intent = self.__build_intent(context)
            context.stdout.write("[color blue]%s[/color]\n" % intent.toUri(0))
            if self.type == "receiver":
                context.getContext().sendBroadcast(intent)
            elif self.type == "activity":
                context.getContext().startActivity(intent)
            elif self.type == "service":
                context.getContext().startService(intent)
        except:
            context.stderr.write("Failed executing intent: %s\n" % sys.exc_info()[1])
    
class FuzzerPackageManager(common.PackageManager.PackageManagerProxy):

    def get_receivers(self, packageNameString):
        receivers = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_RECEIVERS).receivers
        if (str(receivers) == 'null'):
            return None
        else:
            result = []
            for receiver in receivers:
                result.append(str(receiver.name))
            return result
        
    def get_activities(self, packageNameString):
        activities = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_ACTIVITIES).activities
        if (str(activities) == 'null'):
            return None
        else:
            result = []
            for activity in activities:
                result.append(str(activity.name))
            return result
        
    def get_services(self, packageNameString):
        services = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_SERVICES).services
        if (str(services) == 'null'):
            return None
        else:
            result = []
            for service in services:
                result.append(str(service.name))
            return result
