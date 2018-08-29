from data import DataType, getRandomData
import radamsa

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
