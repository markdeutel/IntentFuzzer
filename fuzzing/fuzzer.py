from drozer.modules import common, Module
from drozer import android

import json
import random
import string
import sys

class IntentFuzzer(Module, common.PackageManager):
    name = "Intent fuzzer"
    description = "Android intent fuzzing module "
    examples = ""
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "2018-08-10"
    license = "3 clause BSD"
    path = ["fuzzing"]
    
    staticSource = "/home/mark/deepthought/bachelor/output.json"
    
    def add_arguments(self, parser):
        parser.add_argument("packageName")
    
    def execute(self, arguments):
        templates = self.__build_intent_templates(arguments.packageName)
        for template in templates:
            self.__execute_intent(template)

    def __build_intent_templates(self, packageName):
        templates = []
        datastore = self.__get_static_datastore(IntentFuzzer.staticSource)
        packageInfo = self.packageManager().getPackageInfo(packageName, 
                                                           common.PackageManager.GET_ACTIVITIES |
                                                           common.PackageManager.GET_SERVICES |
                                                           common.PackageManager.GET_RECEIVERS)
        for activityInfo in packageInfo.activities + packageInfo.receivers:
            template = IntentTemplate(type="activity", component=(str(activityInfo.packageName), str(activityInfo.name)), extras=[], bundle=[])
            staticData = datastore.get(str(activityInfo.name))
            if staticData == None:
                staticData = datastore.get(str(activityInfo.targetActivity))
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
            template.printIntent(self)
            if template.type == "activity":
                self.getContext().startActivity(template.buildIntent(self))
            elif template.type == "service":
                self.getContext().startService(template.buildIntent(self))
            else:
                self.stderr.write("Template has invalid type: expected 'activity' or 'service', found %s" % template.type)
        except:
            self.stderr.write("Failed executing intent: %s\n" % sys.exc_info()[1])

class IntentTemplate:
    def __init__(self, type="activity", component=None, extras=None, bundle=None):
        self.type = type
        self.component = component
        self.extras = extras
        self.bundle = bundle
        
    def printIntent(self, context):
        if self.component != None:
            context.stdout.write("type: %s package: %s component: %s extras: " % (self.type, self.component[0], self.component[1]))
            if self.extras != None:
                for invoc in self.extras:
                    context.stdout.write("returnType: %s name: %s " % invoc)
            context.stdout.write("bundle: ")
            if self.bundle != None:
                for invoc in self.bundle:
                    context.stdout.write("returnType: %s name: %s " % invoc)
            context.stdout.write("\n")
    
    def buildIntent(self, context):
        intent = context.new("android.content.Intent")
        self.__set_component_to(intent, context)
        self.__set_extra_to(intent, context)
        self.__set_bundle_extra_to(intent, context)
        return intent;
       
    def __set_component_to(self, intent, context):
        if self.component != None:
            com = context.new("android.content.ComponentName", *self.component)
            intent.setComponent(com)
    
    def __set_extra_to(self, intent, context):
        if self.extras != None:
            for invoc in self.extras:
                if invoc[0] == "boolean":
                    intent.putExtra(invoc[1], context.arg(random.choice[True, False], obj_type="boolean")) 
                elif invoc[0] == "char":
                    intent.putExtra(invoc[1], context.arg(self.__random_str(1), obj_type="char")) 
                elif invoc[0] == "double":
                    intent.putExtra(invoc[1], context.arg(random.uniform(-1000, 1000), obj_type="double")) 
                elif invoc[0] == "float":
                    intent.putExtra(invoc[1], context.arg(random.uniform(-1000, 1000), obj_type="float")) 
                elif invoc[0] == "integer":
                    intent.putExtra(invoc[1], context.arg(random.randint(-1000, 1000), obj_type="integer")) 
                elif invoc[0] == "long":
                    intent.putExtra(invoc[1], context.arg(random.randint(-1000, 1000), obj_type="long")) 
                elif invoc[0] == "short":
                    intent.putExtra(invoc[1], context.arg(random.randint(-1000, 1000), obj_type="short")) 
                elif invoc[0] == "string":
                    intent.putExtra(invoc[1], context.arg(self.__random_str(random.randint(10, 100)), obj_type="string"))
                    
    def __set_bundle_extra_to(self, intent, context):
        if self.bundle != None:
            bundleObj = context.new("android.os.Bundle")
            for invoc in self.bundle:
                if invoc[0] == "boolean":
                    bundleObj.putBoolean(invoc[1], context.arg(random.choice[True, False], obj_type="boolean"))
                elif invoc[0] == "char":
                    bundleObj.putChar(invoc[1], context.arg(self.__random_str(1), obj_type="char"))
                elif invoc[0] == "double":
                    bundleObj.putDouble(invoc[1], context.arg(random.uniform(-1000, 1000), obj_type="double"))
                elif invoc[0] == "float":
                    bundleObj.putFloat(invoc[1], context.arg(random.uniform(-1000, 1000), obj_type="float"))
                elif invoc[0] == "integer":
                    bundleObj.putInt(invoc[1], context.arg(random.randint(-1000, 1000), obj_type="int"))
                elif invoc[0] == "long":
                    bundleObj.putLong(invoc[1], context.arg(random.randint(-1000, 1000), obj_type="long"))
                elif invoc[0] == "short":
                    bundleObj.putShort(invoc[1], context.arg(random.randint(-1000, 1000), obj_type="short"))
            intent.putExtras(bundleObj)
                    
    def __random_str(self, size=8):
        return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(size))
