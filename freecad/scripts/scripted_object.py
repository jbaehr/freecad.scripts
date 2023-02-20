"""
This module defines the "Scripted Object" document object
"""

import sys
import FreeCAD as App


def make_shapeless_object(name):
    """make_shapeless_object(name): make a scripted object without shape."""
    obj = App.ActiveDocument.addObject("App::FeaturePython", name)
    _ScriptedObject(obj)
    return obj


def make_3d_object(name):
    """make_3d_object(name): make a scripted object with a 3D shape."""
    obj = App.ActiveDocument.addObject("Part::FeaturePython", name)
    _ScriptedObject(obj)
    return obj


class _ScriptedObject:
    """The document object proxy for "Scripted Objects"."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyString", "Definition", "Script",
            "The definition of this script, i.e. python code.")

    def execute(self, obj):
        code = compile(obj.Definition, obj.Name, "exec")
        module = type(sys)(obj.Name)
        exec(code, module.__dict__)
        module.execute(obj)

