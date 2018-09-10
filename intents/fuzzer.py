from drozer.modules import common, Module
from drozer.modules.common import loader

from os import path
from time import sleep

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
        parser.add_argument("-n", "--numIter", help="specify the number of itertaion a campaign against a package should take")

    def execute(self, arguments):
        # read cofig
        config = self.__load_json(path.abspath(path.dirname(__file__)) + "/config.json")
        dataStorePath = path.expanduser(config.get("dataStore", path.abspath(path.dirname(__file__))))
        outputPath = path.expanduser(config.get("outputFolder", path.abspath(path.dirname(__file__))))
        androidSDK = path.expanduser(config.get("androidSDK", "~/Android/SDK"))
        
        # get static data from file
        templates = []
        dataStore = self.__load_json(dataStorePath + arguments.packageName + ".json")
        metaStore = self.__load_json(dataStorePath + arguments.packageName + ".meta")
        packageManager = FuzzerPackageManager(self)
        
        # build the intent templates
        for receiver in packageManager.get_receivers(arguments.packageName):
            receiverName = str(receiver.name).encode("utf-8")
            templates.append(self.__build_template(dataStore, metaStore, receiverName, "receiver", (arguments.packageName, receiverName)))

        # activities might have an alias name declared for them. If this is true, the all found static data for this component 
        # is located under the real name not the alias
        for activity in packageManager.get_activities(arguments.packageName):
            targetActivityName = str(activity.targetActivity).encode("utf-8")
            activityName = str(activity.name).encode("utf-8")
            if targetActivityName != "null":
                templates.append(self.__build_template(dataStore, metaStore, targetActivityName, "activity", (arguments.packageName, activityName)))
            else:
                templates.append(self.__build_template(dataStore, metaStore, activityName, "activity", (arguments.packageName, activityName)))

        for service in packageManager.get_services(arguments.packageName):
            serviceName = str(service.name).encode("utf-8")
            templates.append(self.__build_template(dataStore, metaStore, serviceName, "service", (arguments.packageName, serviceName)))

        # send all intents
        IntentBuilder = self.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__)
        logcat.flush_logcat(self, androidSDK)
        for i in xrange(int(arguments.numIter)):
            for template in templates:
                template.send(self, IntentBuilder)
                sleep(1)
        logcat.dump_logcat(self, androidSDK, outputPath + arguments.packageName + ".log")
    
    def __build_template(self, dataStore, metaStore, locator, type, component):
        staticData = json.dumps(dataStore.get(locator, "{}"))
        metaData = json.dumps(metaStore.get(locator, "{}"))
        return IntentTemplate(staticData, metaData, type, component)
    
    def __load_json(self, filePath):
        try:
            with open(filePath, 'r') as file:
                return json.load(file)
        except:
            self.stderr.write("Failed reading static analysis data: %s\n" % sys.exc_info()[1])
    
class IntentTemplate:
    
    def __init__(self, staticData, metaData, type, component):
        self.staticData = staticData
        self.metaData = metaData
        self.component = component
        self.type = type
        
    def send(self, context, IntentBuilder):
        try:
            intentBuilder = context.new(IntentBuilder)
            intent = intentBuilder.build(self.component[0], self.component[1], self.staticData, self.metaData)
            
            context.stdout.write("[color blue]%s[/color]\n" % str(intent.toString()).encode('utf-8'))
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
            return receivers
        
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
            return services
