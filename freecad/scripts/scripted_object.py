"""
This module defines the "Scripted Object" document object
"""

import abc
import sys
import FreeCAD as App
from FreeCAD import Console

if App.GuiUp:
    import FreeCADGui as Gui
    from . import ICON_PATH


def make_shapeless_object(name):
    """Make a scripted object without shape."""
    return _make_object("App::FeaturePython", name)


def make_2d_object(name):
    """Make a scripted object with a 2D shape."""
    return _make_object("Part::Part2DObjectPython", name)


def make_3d_object(name):
    """Make a scripted object with a 3D shape."""
    return _make_object("Part::FeaturePython", name)


def _make_object(fctype, name):
    """Make a scripted object with using fctype as base."""
    obj = App.ActiveDocument.addObject(fctype, name)
    _ScriptedObject(obj)
    if App.GuiUp:
        _ViewProviderScriptedObject(obj.ViewObject)
        _assign_parent(obj)

    return obj


def _assign_parent(obj):
    """Assigns the given objct to the currnetly "active" parent, if any.

    This is requried to have the new object automatically as child of the
    "active body" (when using PartDesign) or in the "active part" (std_part).
    """
    active_parent = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody") \
        or Gui.ActiveDocument.ActiveView.getActiveObject("part")
    if active_parent:
        active_parent.Group += [obj]


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


class _ViewProviderScriptedObject:
    """
    View object proxy for _ScriptedObject
    """

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        """Hook when Proxy is assigned; after init and when loaded from disc."""
        self.Object = vobj.Object

    def getIcon(self):
        # Depending which FreeCAD Core Object is scripted, we return a different icon.
        # Note that the order of the checks matters, see the relationships of core objects
        # in the niheritence diagram here: https://wiki.freecad.org/App_DocumentObject
        icon = "script-2d-shape.svg" if self.Object.isDerivedFrom("Part::Part2DObjectPython") else \
            "script-3d-shape.svg" if self.Object.isDerivedFrom("Part::FeaturePython") else \
            "script-no-shape.svg"
        # TODO add support for pathlib to FreeCAD to get rid of this extra `str(...)`
        return str(ICON_PATH / icon)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        pass


def gui_command(name):
    """
    Decorator for command classes to register an instance of them automatically.
    """
    def registrar(command_class):
        if App.GuiUp:
            Gui.addCommand(name, command_class())
        return command_class

    return registrar


class _Command(abc.ABC):
    """
    Base class for declarative commands.

    Derived classes just have to define attribtues, the rest of the magic happens here.
    """

    def GetResources(self):
        resources = {
            'MenuText': getattr(self, 'MenuText', self.__class__.__name__),
            'ToolTip': getattr(self, 'ToolTip', self.__doc__),
            }

        if hasattr(self, 'Icon'):
            # TODO add support for pathlib to FreeCAD to get rid of this extra `str(...)`
            resources['Pixmap'] = str(ICON_PATH / self.Icon)

        return resources

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        if not hasattr(self, 'Function'):
            raise NotImplementedError(
                "If no 'Function' attribute is defined, this methods needs to be implemented.")

        transaction_name = getattr(self, 'Transaction', None)
        if transaction_name:
            App.ActiveDocument.openTransaction(transaction_name)

        module = self.Function.__module__
        function = self.Function.__name__
        args = [repr(arg) for arg in getattr(self, 'Args', [])]
        command = f"{module}.{function}({', '.join(args)})"
        Gui.addModule(module)
        Gui.doCommand(command)


@gui_command('Scripts_ShapelessObject')
class _ShapelessObject(_Command):
    MenuText = "Shapeless Object"
    ToolTip = "Create a new 'Scripted Object' without a shape."
    Icon = "script-no-shape.svg"

    Transaction = "Create Scripted Object"
    Function = make_shapeless_object
    Args = ["ScriptedObject"]


@gui_command('Scripts_2DObject')
class _2DObject(_Command):
    MenuText = "2D Object"
    ToolTip = "Create a new 'Scripted Object' with a 2D shape."
    Icon = "script-2d-shape.svg"

    Transaction = "Create Scripted 2D Object"
    Function = make_2d_object
    Args = ["Scripted2DObject"]


@gui_command('Scripts_3DObject')
class _3DObject(_Command):
    MenuText = "3D Object"
    ToolTip = "Create a new 'Scripted Object' with a 3D shape."
    Icon = "script-3d-shape.svg"

    Transaction = "Create Scripted 3D Object"
    Function = make_3d_object
    Args = ["Scripted3DObject"]
