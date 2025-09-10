"""Compatibility layer for moved auth package."""
import sys
from importlib import import_module

_module = import_module("heartlytics.auth")
sys.modules[__name__] = _module
