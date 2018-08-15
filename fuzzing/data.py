from enum import Enum
from functools import partial

import random
import string

class DataType(Enum):
    BOOL = "boolean"
    INT = "integer"
    LONG = "long"
    SHORT = "short"
    DOUBLE = "float"
    FLOAT = "float"
    CHAR = "char"
    STR = "string"

def __random_str():
    return ''.join(random.choice(string.printable) for x in range(random.randint(10, 100)))

randomTypeLookup = {
    DataType.BOOL: partial(random.choice, [True, False]),
    DataType.INT: partial(random.randint, -1000, 1000),
    DataType.LONG: partial(random.randint, -1000, 1000),
    DataType.SHORT: partial(random.randint, -1000, 1000),
    DataType.DOUBLE: partial(random.uniform, -1000, 1000),
    DataType.FLOAT: partial(random.uniform, -1000, 1000),
    DataType.CHAR: partial(random.choice, string.printable),
    DataType.STR: partial(__random_str)
}

def getRandomData(context, type=DataType.INT, array=False):    
    if array != True:
        return context.arg(randomTypeLookup.get(type)(), obj_type=type.value)
    else:
        arr = []
        for i in range(random.randint(10, 100)):
            arr.append(randomTypeLookup.get(type)())
        return context.arg(arr)
