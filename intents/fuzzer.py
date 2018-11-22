from drozer.modules import common, Module
from drozer.modules.common import loader
from pydiesel.reflection import ReflectionException

from os import path
from time import sleep
from config import Config
from template import IntentTemplate
from packagemanager import FuzzerPackageManager

import signal
import logcat
import json
import sys

import atexit

class Fuzzer(Module, loader.ClassLoader):

    name = "Intent Fuzzer"
    description = "This module is used to generate fuzzed intents and send them."
    examples = "Use config.json file to configure the fuzzer"
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "05.09.2018"
    license = "BSD (3-clause)"
    path = ["intents"]
    
    logcat_proc = None
    
    def signal_handler(self, sig, frame):
        if self.logcat_proc != None:
            self.stdout.write("\nKilling logcat subprocess.\n")
            self.logcat_proc.kill();
        raise KeyboardInterrupt()
    
    def atexit_handler(self):
        if self.logcat_proc != None:
            self.stdout.write("Killing logcat subprocess.\n")
            self.logcat_proc.kill();

    def add_arguments(self, parser):
        pass

    def execute(self, arguments):
        # add some handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        atexit.register(self.atexit_handler)
        
        # read cofig
        try:
            config = Config()
            for packageName in config.packageNames:
                try:
                    self.__test_package(config, packageName)
                except Exception as ex1:
                    self.stderr.write("[color red]Failed testing application package: %s, %s[/color]\n" % (packageName, str(ex1)))
        except Exception as ex2:
            self.stderr.write("[color red]Failed loading config file: %s[/color]\n" % str(ex2))
        
    def __test_package(self, config, packageName):        
        # print header
        self.stdout.write("\n")
        self.stdout.write("[color red]%s[/color]\n" % packageName)
        self.stdout.write("[color red]--------------------------------------------------------------------------------[/color]\n")
        
        # get static data from file
        templates = []
        dataStore = self.__load_json(config.dataStorePath + packageName + ".json")
        metaStore = self.__load_json(config.dataStorePath + packageName + ".meta")
        strgStore = self.__load_strg(config.dataStorePath + packageName + ".str", 300)
        
        # get IntentBuilder instance
        intentBuilder = self.new(self.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__), json.dumps(strgStore))
        
        # build the intent templates
        packageManager = FuzzerPackageManager(self)
        receivers = packageManager.get_receivers(packageName)
        self.stdout.write("Found %s exported receivers\n" % len(receivers))
        for receiver in receivers:
            receiverName = str(receiver.name).encode("utf-8")
            self.__build_template(intentBuilder, templates, dataStore, metaStore, receiverName, "receiver", (packageName, receiverName))

        # activities might have an alias name declared for them. If this is true, the all found static data for this component 
        # is located under the real name not the alias
        activities = packageManager.get_activities(packageName)
        self.stdout.write("Found %s exported activities\n" % len(activities))
        for activity in activities:
            targetActivityName = str(activity.targetActivity).encode("utf-8")
            activityName = str(activity.name).encode("utf-8")
            if targetActivityName != "null":
                self.__build_template(intentBuilder, templates, dataStore, metaStore, targetActivityName, "activity", (packageName, activityName))
            else:
                self.__build_template(intentBuilder, templates, dataStore, metaStore, activityName, "activity", (packageName, activityName))

        services = packageManager.get_services(packageName)
        self.stdout.write("Found %s exported services\n" % len(services))
        for service in services:
            serviceName = str(service.name).encode("utf-8")
            self.__build_template(intentBuilder, templates, dataStore, metaStore, serviceName, "service", (packageName, serviceName))

        # send all intents
        appFilePath = config.outputPath + packageName + ".app.log"
        crashFilePath = config.outputPath + packageName + ".crash.log"
        self.logcat_proc = logcat.logcat_listen(self, appFilePath, config.androidSDK)
        logcat.write_log_entry(self, "Packagename: " + packageName)
        logcat.write_log_entry(self, "Number of iterations: " + str(config.numIter)) 
        logcat.write_log_entry(self, "Exported receivers: " + str(len(receivers)))
        logcat.write_log_entry(self, "Exported activities: " + str(len(activities)))
        logcat.write_log_entry(self, "Exported services: " + str(len(services)))        
        for i in xrange(config.numIter):
            self.stdout.write("[color blue]Iteration: %d --------------------------------------------------------------------------------[/color]\n" % (i + 1))
            for template in templates:
                try:
                    context = self.getContext();
                    self.stdout.write("%s\n" % template.toString())
                    template.send(context)
                    sleep(config.intentTimeout)
                    template.killProcess(context)
                except  Exception as e:
                    self.stderr.write("[color red]Failed sending intent: %s[/color]\n" % str(e))
        self.logcat_proc.kill();
    
    def __build_template(self, intentBuilder, templates, dataStore, metaStore, locator, type, component):
        staticData = json.dumps(dataStore.get(locator, {}))
        metaData = metaStore.get(locator, {})
        categories = metaData.get("categories", [])
        actions = metaData.get("actions", [])
        data = metaData.get("data", [])
        for action in actions:
            templates.append(IntentTemplate(intentBuilder, staticData, type, component, action, categories, data))
        # Even if there is no expected action defined in the intent filter: 
        # There is always the possibility to directly send an intent to a component.
        templates.append(IntentTemplate(intentBuilder, staticData, type, component, "null", categories, data))
    
    def __load_json(self, filePath):
        with open(filePath, 'r') as file:
            return json.load(file)
        
    def __load_strg(self, filePath, maxElm):
        with open(filePath, 'r') as file:
            count = 0;
            strgStore = [];
            for line in file:
                if count > maxElm:
                    break
                line = line.decode('iso-8859-1')
                strgStore.append(line.rstrip())
            return strgStore
