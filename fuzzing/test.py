from drozer.modules import common, Module
from drozer.modules.common import loader
from drozer import android
from template import IntentTemplate

import radamsa

class Test(Module, loader.ClassLoader):
    name = "test"
    description = "test"
    examples = ""
    author = "Mark Deutel <mark.deutel@fau.de>"
    date = "2018-08-10"
    license = "3 clause BSD"
    path = ["fuzzing"]
    
    def execute(self, arguments):
        intentBuilder = self.new(self.loadClass("IntentBuilder.apk", "IntentBuilder", relative_to=__file__))
        intentBuilder.createIntent("com.android.chrome", "MainActivity");
        intentBuilder.putExtra("integer", "dummyNuber", radamsa.next("integer"))
        intent = intentBuilder.getIntent()
        self.stdout.write("%s\n" % intent.toUri(0))
