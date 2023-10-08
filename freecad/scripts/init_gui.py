import FreeCADGui as Gui
import FreeCAD as App
from . import ICON_PATH


class ScriptsWorkbench(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    MenuText = "Scripts"
    ToolTip = "Python Scripts as Document Objects"
    Icon = str(ICON_PATH / "scripts-workbench.svg") # TODO add support for pathlib to FreeCAD
    toolbox = []

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        from . import scripted_object
        self.toolbox.append('Scripts_ShapelessObject')
        self.toolbox.append('Scripts_3DObject')
        self.toolbox.append('Scripts_2DObject')

        self.appendToolbar("Scripts", self.toolbox)
        self.appendMenu("Scripts", self.toolbox)

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        pass

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        pass


Gui.addWorkbench(ScriptsWorkbench())
