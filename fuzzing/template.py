from drozer.modules import common
import json
import radamsa

def build_intent_templates(context, packageName):
    templates = []
    datastore = __get_static_datastore(context, "/home/mark/deepthought/bachelor/datastore/" + packageName + ".json")
    packageInfo = context.packageManager().getPackageInfo(packageName, 
                                                        common.PackageManager.GET_ACTIVITIES |
                                                        common.PackageManager.GET_SERVICES |
                                                        common.PackageManager.GET_RECEIVERS)
    for activityInfo in packageInfo.activities:
        template = IntentTemplate(type="activity", component=(str(activityInfo.packageName), str(activityInfo.name)), extras=[], bundle=[])
        staticData = datastore.get(str(activityInfo.name))
        if staticData == None:
            staticData = datastore.get(str(activityInfo.targetActivity))
        if staticData != None:
            template.extras = __extract_invocations(staticData, "extras")
            template.bundle = __extract_invocations(staticData, "bundle")
        templates.append(template)
    for receiverInfo in packageInfo.receivers:
        template = IntentTemplate(type="broadcast", component=(str(receiverInfo.packageName), str(receiverInfo.name)), extras=[], bundle=[])
        staticData = datastore.get(str(receiverInfo.name))
        if staticData == None:
            staticData = datastore.get(str(receiverInfo.targetActivity))
        if staticData != None:
            template.extras = __extract_invocations(staticData, "extras")
            template.bundle = __extract_invocations(staticData, "bundle")
        templates.append(template)
    for serviceInfo in packageInfo.services:
        template = IntentTemplate(type="service", component=(str(serviceInfo.packageName), str(serviceInfo.name)), extras=[], bundle=[])
        staticData = datastore.get(str(serviceInfo.name))
        if staticData != None:
            template.extras = __extract_invocations(staticData, "extras")
            template.bundle = __extract_invocations(staticData, "bundle")
        templates.append(template)
    context.stdout.write("Created %i intent templates\n" % len(templates))
    return templates
    
def __get_static_datastore(context, source):
    try:
        with open(source, 'r') as file:
            return json.load(file)
    except:
        context.stderr.write("Failed reading static analysis data: %s\n" % sys.exc_info()[1])
        return None
        
def __extract_invocations(staticData, field):
    invocations = []
    for invocation in staticData[field]:
        returnType = invocation["returnType"]
        value = invocation["value"]
        invocations.append((returnType, value))
    return invocations

class IntentTemplate:
    def __init__(self, type="activity", component=None, extras=None, bundle=None):
        self.type = type
        self.component = component
        self.extras = extras
        self.bundle = bundle
    
    def buildIntent(self, context):
        intentBuilder = context.new(context.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__))
        intentBuilder.createIntent(self.component[0], self.component[1])
        
        if self.extras != None:
            for extra in self.extras:
                intentBuilder.putExtra(extra[0], extra[1], radamsa.next(extra[0]))
                
        if self.bundle != None:
            intentBuilder.createBundle()
            for item in self.bundle:
                intentBuilder.putBundleExtra(item[0], item[1])
            intentBuilder.applyBundleToIntent()
        
        intent = intentBuilder.getIntent()
        context.stdout.write("%s\n" % intent.toUri(0))
        return intent
    
    def __print_intent(self, context):
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
