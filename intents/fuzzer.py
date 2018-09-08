from drozer.modules import common, Module
from drozer.modules.common import loader

import logcat
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
        parser.add_argument("-o", "--logcatOutputPath", help="specify a path on your local machine where all logcat output is dumped.")
        parser.add_argument("-n", "--numIter", help="specify the number of itertaion a campaign against a package should take")

    def execute(self, arguments):
        # get static data from file
        templates = []
        dataStore = self.__load_data_store(arguments.staticData)
        packageManager = FuzzerPackageManager(self)
        
        # build the intent templates
        for receiver in packageManager.get_receivers(arguments.packageName):
            templates.append(self.__build_template(dataStore, receiver, "receiver", (arguments.packageName, receiver)))

        # activities might have an alias name declared for them. If this is true, the all found static data for this component 
        # is located under the real name not the alias
        for activity in packageManager.get_activities(arguments.packageName):
            if str(activity.targetActivity) != "null":
                templates.append(self.__build_template(dataStore, str(activity.targetActivity), "activity", (arguments.packageName, str(activity.name))))
            else:
                templates.append(self.__build_template(dataStore, str(activity.name), "activity", (arguments.packageName, str(activity.name))))

        for service in packageManager.get_services(arguments.packageName):
            templates.append(self.__build_template(dataStore, service, "service", (arguments.packageName, service)))

        # send all intents
        logcat.flush_logcat(self)
        IntentBuilder = self.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__)
        for i in xrange(int(arguments.numIter)):
            for template in templates:
                template.send(self, IntentBuilder)
        logcat.dump_logcat(self, arguments.logcatOutputPath)
    
    def __build_template(self, dataStore, locator, type, component):
        staticData = json.dumps(dataStore.get(locator, "{}"))
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
        
    def send(self, context, IntentBuilder):
        try:
            intentBuilder = context.new(IntentBuilder)
            intent = intentBuilder.build(self.component[0], self.component[1], self.staticData)
            
            context.stdout.write("[color blue]%s[/color]\n" % intent.toString())
            extraStr = intentBuilder.getExtrasString(intent)
            if str(extraStr) != "null":
                context.stdout.write("[color green]%s[/color]\n" % extraStr)
            
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
        if str(receivers) == "null":
            return None
        else:
            result = []
            for receiver in receivers:
                result.append(str(receiver.name))
            return result
        
    def get_activities(self, packageNameString):
        activities = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_ACTIVITIES).activities
        if str(activities) == "null":
            return None
        else:
            return activities
        
    def get_services(self, packageNameString):
        services = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_SERVICES).services
        if str(services) == "null":
            return None
        else:
            result = []
            for service in services:
                result.append(str(service.name))
            return result
