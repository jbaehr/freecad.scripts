"""
This module defines the "Scripted Object" document object
"""

import sys
import FreeCAD as App
from FreeCAD import Console


def make_shapeless_object(name):
    """make_shapeless_object(name): make a scripted object without shape."""
    obj = App.ActiveDocument.addObject("App::FeaturePython", name)
    _ScriptedObject(obj)
    return obj


def make_2d_object(name):
    """make_2d_object(name): make a scripted object with a 2D shape."""
    obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", name)
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
        obj.addProperty("App::PropertyBool", "AllowExecution", "Script",
            "Allow the execution of this script. Do this only if the source is trustworthy!")
        obj.setPropertyStatus("AllowExecution", "Transient")
        obj.AllowExecution = True # if we just create the sript, we trust ourself

    def onDocumentRestored(self, obj):
        # per default, block execution when loading from disk: we don't know if it's trustworthy.
        # TODO: check allow list in user settings
        obj.AllowExecution = False
        # As expressions override persisted property values, we have to make sure that a malicious
        # document does not trick us into execution that way.
        obj.setExpression("AllowExecution", None)

    def execute(self, obj):
        if not obj.AllowExecution:
            Console.PrintError(f"Execution of script {obj.Name} is not allowed\n")
            return
        code = compile(obj.Definition, obj.Name, "exec")
        module = type(sys)(obj.Name)
        exec(code, module.__dict__)
        module.execute(obj)

