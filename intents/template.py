import json

class IntentTemplate:
    
    def __init__(self, intentBuilder, staticData, type, component, action, categories, data):
        self.intentBuilder = intentBuilder
        self.staticData = staticData
        self.template = {}
        self.template["type"] = type
        self.template["component"] = component
        self.template["action"] = action
        self.template["categories"] = categories
        self.template["data"] = data;
        
    def send(self, context):
        intent = self.intentBuilder.build(json.dumps(self.template), self.staticData)
        if self.template["type"] == "activity":
            context.startActivity(intent)
        elif self.template["type"] == "service":
            context.startService(intent)
        elif self.template["type"] == "receiver":
            context.sendBroadcast(intent)
            
    def killProcess(self, context):
        activityManager = context.getSystemService(context.ACTIVITY_SERVICE)
        if activityManager != "null":
            activityManager.killBackgroundProcesses(self.template["component"][0])
            
    def toString(self):
        sb = ["type: ", self.template["type"], " component: ", self.template["component"][0], "/", 
              self.template["component"][1], " action: ", self.template["action"]];
        return "".join(sb)
