"""Compatibility layer for moved services package."""
import sys
from importlib import import_module

_module = import_module("heartlytics.services")
sys.modules[__name__] = _module
