from drozer.modules import common, Module
from drozer import android

import os

class ListFiles(Module, common.ClassLoader, common.FileSystem):

    name = "listfiles"
    description = ""
    examples = ""
    author = "Mark Deutel"
    date = "2018-08-03"
    license = "BSD (3-clause)"
    path = ["utils"]
    
    def add_arguments(self, parser):
        parser.add_argument("target")

    def execute(self, arguments):
        files = self.listFiles(arguments.target)
        for file in files:
            self.stdout.write("%s\n" % file)
