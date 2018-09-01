from drozer.modules import common, Module
from drozer.modules.common import loader
from template import IntentTemplate, build_intent_templates

import logcat
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
        parser.add_argument("-p", "--packageName", help="specify the package which should be attacked.")
        parser.add_argument("-n", "--numIter", default=1, help="specify the number of iterations for this campaign.")
        parser.add_argument("-o", "--outputPath", default="~/output.log", help="specify a location on the host computers file system where the logcat output should be stored.")
    
    def execute(self, arguments):
        logcat.flush_logcat(self)
        templates = build_intent_templates(self, arguments.packageName)
        for i in xrange(int(arguments.numIter)):
            for template in templates:
                logcat.write_log_entry(self, "Running intent: " + template.component[0] + template.component[1])
                self.__execute_intent(template)
        logcat.dump_logcat(self, arguments.outputPath)
    
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
