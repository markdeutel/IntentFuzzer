from data import RandomData

import random
import string

class IntentTemplate:
    def __init__(self, type="activity", component=None, extras=None, bundle=None):
        self.type = type
        self.component = component
        self.extras = extras
        self.bundle = bundle
    
    def buildIntent(self, context):
        intent = context.new("android.content.Intent")
        self.__set_component_to(intent, context)
        self.__set_extra_to(intent, context)
        self.__set_bundle_extra_to(intent, context)
        self.__print_intent(context)
        return intent;
    
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
       
    def __set_component_to(self, intent, context):
        if self.component != None:
            com = context.new("android.content.ComponentName", *self.component)
            intent.setComponent(com)
    
    def __set_extra_to(self, intent, context):
        if self.extras != None:
            for invoc in self.extras:
                if invoc[0] == "boolean":
                    intent.putExtra(invoc[1], context.arg(random.choice([True, False]), obj_type="boolean")) 
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
