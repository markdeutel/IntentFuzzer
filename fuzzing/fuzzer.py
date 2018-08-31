from drozer.modules import common, Module
from drozer.modules.common import loader
from template import IntentTemplate, build_intent_templates
import sys

class IntentFuzzer(Module, common.PackageManager, loader.ClassLoader):
    name = "Intent fuzzer"
    description = "Android intent fuzzing module"
    examples = ""
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "2018-08-10"
    license = "3 clause BSD"
    path = ["fuzzing"]
    
    def add_arguments(self, parser):
        parser.add_argument("packageName")
        parser.add_argument("numIter")
    
    def execute(self, arguments):
        templates = build_intent_templates(self, arguments.packageName)
        for i in xrange(int(arguments.numIter)):
            for template in templates:
                self.__execute_intent(template)
    
    def __execute_intent(self, template):
        try:
            if template.type == "activity":
                self.getContext().startActivity(template.buildIntent(self))
            elif template.type == "service":
                self.getContext().startService(template.buildIntent(self))
            elif template.type == "broadcast":
                self.getContext().sendBroadcast(template.buildIntent(self))
        except:
            self.stderr.write("Failed executing intent: %s\n" % sys.exc_info()[1])
