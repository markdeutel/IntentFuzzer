from drozer.modules import common, Module
from drozer.modules.common import loader
from pydiesel.reflection import ReflectionException

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
        configPath = path.abspath(path.dirname(__file__)) + "/config.json"
        self.stdout.write("Loading config file: %s\n" % configPath)
        config = Config(self.__load_json(configPath))
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
        strgStore = self.__load_strg(config.dataStorePath + packageName + ".str", 500)
        if dataStore == None or metaStore == None:
            self.stderr.write("Could not find data from static analysis\n")
            return;
        
        # get ProcessManager and IntentBuilder instance
        processManager = self.new(self.loadClass("ProcessManager.apk", "ProcessManager", relative_to=__file__))
        intentBuilder = self.new(self.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__), json.dumps(strgStore))
        
        # build the intent templates
        packageManager = FuzzerPackageManager(self)
        receivers = packageManager.get_receivers(packageName)
        self.stdout.write("Found %s exported receivers\n" % len(receivers))
        for receiver in receivers:
            receiverName = str(receiver.name).encode("utf-8")
            self.__build_template(intentBuilder, processManager, templates, dataStore, metaStore, receiverName, "receiver", (packageName, receiverName))

        # activities might have an alias name declared for them. If this is true, the all found static data for this component 
        # is located under the real name not the alias
        activities = packageManager.get_activities(packageName)
        self.stdout.write("Found %s exported activities\n" % len(activities))
        for activity in activities:
            targetActivityName = str(activity.targetActivity).encode("utf-8")
            activityName = str(activity.name).encode("utf-8")
            if targetActivityName != "null":
                self.__build_template(intentBuilder, processManager, templates, dataStore, metaStore, targetActivityName, "activity", (packageName, activityName))
            else:
                self.__build_template(intentBuilder, processManager, templates, dataStore, metaStore, activityName, "activity", (packageName, activityName))

        services = packageManager.get_services(packageName)
        self.stdout.write("Found %s exported services\n" % len(services))
        for service in services:
            serviceName = str(service.name).encode("utf-8")
            self.__build_template(intentBuilder, processManager, templates, dataStore, metaStore, serviceName, "service", (packageName, serviceName))

        # send all intents
        appFilePath = config.outputPath + packageName + ".app.log"
        crashFilePath = config.outputPath + packageName + ".crash.log"
        logcat_proc = logcat.logcat_listen(self, appFilePath, config.androidSDK)
        logcat.write_log_entry(self, "Packagename: " + packageName)
        logcat.write_log_entry(self, "Number of iterations: " + str(config.numIter)) 
        logcat.write_log_entry(self, "Exported receivers: " + str(len(receivers)))
        logcat.write_log_entry(self, "Exported activities: " + str(len(activities)))
        logcat.write_log_entry(self, "Exported services: " + str(len(services)))
        
        
        appContext = self.getContext()
        
        for i in xrange(config.numIter):
            self.stdout.write("[color blue]Iteration: %d --------------------------------------------------------------------------------[/color]\n" % (i + 1))
            for template in templates:
                try:
                    self.stdout.write("%s\n" % template.toString())
                    template.send(self, appContext)
                    #sleep(config.intentTimeout)
                    template.killProcess(self, appContext)
                    #sleep(2)
                except  Exception as e:
                    self.stderr.write("[color red]Failed executing template: %s[/color]\n" % str(e))
        logcat_proc.kill();
    
    def __build_template(self, intentBuilder, processManager, templates, dataStore, metaStore, locator, type, component):
        staticData = json.dumps(dataStore.get(locator, {}))
        metaData = metaStore.get(locator, {})
        categories = metaData.get("categories", [])
        actions = metaData.get("actions", [])
        data = metaData.get("data", [])
        for action in actions:
            templates.append(IntentTemplate(intentBuilder, processManager, staticData, type, component, action, categories, data))
        # Even if there is no expected action defined in the intent filter: 
        # There is always the possibility to directly send an intent to a component.
        templates.append(IntentTemplate(intentBuilder, processManager, staticData, type, component, "null", categories, data))
    
    def __load_json(self, filePath):
        try:
            with open(filePath, 'r') as file:
                return json.load(file)
        except:
            self.stderr.write("Failed reading json file: %s\n" % sys.exc_info()[1])
            return None
        
    def __load_strg(self, filePath, maxElm):
        try:
            with open(filePath, 'r') as file:
                count = 0;
                strgStore = [];
                for line in file:
                    if count > maxElm:
                        break
                    line = line.decode('iso-8859-1')
                    strgStore.append(line.rstrip())
                return strgStore
        except:
            self.stderr.write("Failed reading string file: %s\n" % sys.exc_info()[1])
            return None
    
class IntentTemplate:
    
    def __init__(self, intentBuilder, processManager, staticData, type, component, action, categories, data):
        self.intentBuilder = intentBuilder
        self.processManager = processManager
        self.staticData = staticData
        self.template = {}
        self.template["type"] = type
        self.template["component"] = component
        self.template["action"] = action
        self.template["categories"] = categories
        self.template["data"] = data;
        
    def send(self, context, appContext):
        try:
            intent = self.intentBuilder.build(json.dumps(self.template), self.staticData)
            self.processManager.sendIntent(appContext, self.template["type"], intent)
        except ReflectionException as e:
            context.stderr.write("[color red]Failed sending intent: %s[/color]\n" % e.message.encode('utf-8'))
            
    def killProcess(self, context, appContext):
        self.processManager.killBackgroundProcess(appContext, self.template["component"][0])
            
    def toString(self):
        sb = ["type: ", self.template["type"], " component: ", self.template["component"][0], "/", 
              self.template["component"][1], " action: ", self.template["action"]];
        return "".join(sb)
            
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
