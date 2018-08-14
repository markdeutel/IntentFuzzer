from enum import Enum
from functools import partial

import random
import string

class DataType(Enum):
    BOOL = 0
    INT = 1
    FLOAT = 2
    CHAR = 3
    STR = 4

def __random_str():
    return ''.join(random.choice(string.printable) for x in range(random.randint(10, 100)))

randomTypeLookup = {
    DataType.BOOL: partial(random.choice, [True, False]),
    DataType.INT: partial(random.randint, -1000, 1000),
    DataType.FLOAT: partial(random.uniform, -1000, 1000),
    DataType.CHAR: partial(random.choice, string.printable),
    DataType.STR: partial(__random_str)
}

def getRandomData(type=DataType.INT, size=1):    
    assert size >= 1
    if size == 1:
        return randomTypeLookup.get(type)()
    else:
        arr = []
        for i in range(size):
            arr.append(randomTypeLookup.get(type)())
        return arr
