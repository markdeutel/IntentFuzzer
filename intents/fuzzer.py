from drozer.modules import common, Module
from drozer.modules.common import loader

from os import path
from time import sleep

import logcat
import logparser
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

    def execute(self, arguments):
        # read cofig
        config = Config(self.__load_json(path.abspath(path.dirname(__file__)) + "/config.json"))
        for packageName in config.packageNames:
            self.__test_package(config, packageName)
        
    def __test_package(self, config, packageName):
        # print header
        self.stdout.write("\n")
        self.stdout.write("[color red]%s[/color]\n" % packageName)
        self.stdout.write("[color red]--------------------------------------------------------------------------------[/color]\n")
        
        # get static data from file
        templates = []
        dataStore = self.__load_json(config.dataStorePath + packageName + ".json")
        metaStore = self.__load_json(config.dataStorePath + packageName + ".meta")
        
        # build the intent templates
        packageManager = FuzzerPackageManager(self)
        receivers = packageManager.get_receivers(packageName)
        self.stdout.write("Found %s exported receivers\n" % len(receivers))
        for receiver in receivers:
            receiverName = str(receiver.name).encode("utf-8")
            templates.append(self.__build_template(dataStore, metaStore, receiverName, "receiver", (packageName, receiverName)))

        # activities might have an alias name declared for them. If this is true, the all found static data for this component 
        # is located under the real name not the alias
        activities = packageManager.get_activities(packageName)
        self.stdout.write("Found %s exported activities\n" % len(activities))
        for activity in activities:
            targetActivityName = str(activity.targetActivity).encode("utf-8")
            activityName = str(activity.name).encode("utf-8")
            if targetActivityName != "null":
                templates.append(self.__build_template(dataStore, metaStore, targetActivityName, "activity", (packageName, activityName)))
            else:
                templates.append(self.__build_template(dataStore, metaStore, activityName, "activity", (packageName, activityName)))

        services = packageManager.get_services(packageName)
        self.stdout.write("Found %s exported services\n" % len(services))
        for service in services:
            serviceName = str(service.name).encode("utf-8")
            templates.append(self.__build_template(dataStore, metaStore, serviceName, "service", (packageName, serviceName)))

        # send all intents
        IntentBuilder = self.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__)
        logcat.flush_logcat(self, config.androidSDK)
        sleep(5)
        logcat.write_log_entry(self, "Packagename: " + packageName)
        logcat.write_log_entry(self, "Number of iterations: " + str(config.numIter)) 
        logcat.write_log_entry(self, "Exported receivers: " + str(len(receivers)))
        logcat.write_log_entry(self, "Exported activities: " + str(len(activities)))
        logcat.write_log_entry(self, "Exported services: " + str(len(services)))
        for i in xrange(config.numIter):
            self.stdout.write("Iteration: %d --------------------------------------------------------------------------------\n" % (i + 1))
            for template in templates:
                template.send(self, IntentBuilder)
                sleep(config.intentTimeout)
                
        appFilePath = config.outputPath + packageName + ".app.log"
        crashFilePath = config.outputPath + packageName + ".crash.log"
        logcat.dump_logcat(self, config.androidSDK, appFilePath, crashFilePath)
    
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
            
            context.stdout.write("[color blue]%s[/color]\n" % str(intent.toString()).encode("utf-8"))
            extraStr = intentBuilder.getExtrasString(intent)
            if str(extraStr) != "null":
                context.stdout.write("[color green]%s[/color]\n" % extraStr)
            logcat.write_log_entry(context, str(intent.toUri(0)).encode("utf-8"))
            
            if self.type == "receiver":
                context.getContext().sendBroadcast(intent)
            elif self.type == "activity":
                context.getContext().startActivity(intent)
            elif self.type == "service":
                context.getContext().startService(intent)
        except:
            context.stderr.write("Failed executing intent: %s\n" % sys.exc_info()[1])
            
class Config:
    
    def __init__(self, jsonConfig):
        self.dataStorePath = path.expanduser(jsonConfig.get("dataStore", path.abspath(path.dirname(__file__))))
        self.outputPath = path.expanduser(jsonConfig.get("outputFolder", path.abspath(path.dirname(__file__))))
        self.androidSDK = path.expanduser(jsonConfig.get("androidSDK", "~/Android/SDK"))
        self.intentTimeout = jsonConfig.get("intentTimeout", 2)
        self.numIter = jsonConfig.get("numberIterations", 1)
        self.packageNames = jsonConfig.get("packageNames", [])
        
    
class FuzzerPackageManager(common.PackageManager.PackageManagerProxy, common.Filters):

    def get_receivers(self, packageNameString):
        receivers = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_RECEIVERS).receivers
        if str(receivers) == "null":
            return []
        else:
            receivers = self.match_filter(receivers, "exported", True)
            return receivers
        
    def get_activities(self, packageNameString):
        activities = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_ACTIVITIES).activities
        if str(activities) == "null":
            return []
        else:
            activities = self.match_filter(activities, "exported", True)
            return activities
        
    def get_services(self, packageNameString):
        services = self.packageManager().getPackageInfo(packageNameString,
                                                         self.packageManager().GET_SERVICES).services
        if str(services) == "null":
            return []
        else:
            services = self.match_filter(services, "exported", True)
            return services
