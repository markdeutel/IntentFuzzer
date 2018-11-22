from os import path
import json

class Config:
    
    def __init__(self):
        configPath = path.abspath(path.dirname(__file__)) + "/config.json"
        with open(configPath, 'r') as file:
            jsonConfig = json.load(file)
            self.dataStorePath = path.expanduser(jsonConfig.get("dataStore", path.abspath(path.dirname(__file__))))
            self.outputPath = path.expanduser(jsonConfig.get("outputFolder", path.abspath(path.dirname(__file__))))
            self.androidSDK = path.expanduser(jsonConfig.get("androidSDK", "~/Android/SDK"))
            self.intentTimeout = jsonConfig.get("intentTimeout", 2)
            self.numIter = jsonConfig.get("numberIterations", 1)
            self.packageNames = jsonConfig.get("packageNames", [])
