import sys
from importlib import import_module
_module = import_module("heartlytics.simulations")
sys.modules[__name__] = _module
