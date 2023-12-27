import numpy as np
from ctypes import *
import os
PATH = os.getcwd()+'\\'

try:
    try:
        try:
            lib = CDLL(PATH+'mazeGenerator.dll')
        except Exception:
            os.system('g++ mazeGenerator.cpp -shared -o mazeGenerator.dll')
            lib = CDLL(PATH+'mazeGenerator.dll')
    except Exception:
        try:
            lib = CDLL(PATH+'mazeGenerator.so')
        except Exception:
            os.system('g++ mazeGenerator.cpp -shared -o mazeGenerator.so')
            lib = CDLL(PATH+'mazeGenerator.so')
except Exception:
    raise ImportError("Cannot Find C extension")


class DataParams(Structure):
    _fields_ = [('data', c_longlong), ('shape', c_longlong)]


def generate(maze):
    assert maze.dimension == 4, "Only 4D mazes can be generated thru C-Scripts"
    shapeArr = np.array(maze.shape, dtype=np.int32)
    param = DataParams(maze.data.ctypes._as_parameter_.value,
                       shapeArr.ctypes._as_parameter_.value)
    lib.generate(byref(param))
