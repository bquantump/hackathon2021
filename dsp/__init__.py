import os

try:
    # this might fail if the module is python-only
    from .dsp import *
except ModuleNotFoundError:
    pass