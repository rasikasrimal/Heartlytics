"""Compatibility layer for moved utils package."""
import sys
from importlib import import_module

_module = import_module("heartlytics.utils")
sys.modules[__name__] = _module
