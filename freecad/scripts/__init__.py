import FreeCAD
import pathlib

RESOURCE_PATH = pathlib.Path(__file__).resolve().parent / "resources"
ICON_PATH = RESOURCE_PATH / "icons"

FreeCAD.__unit_test__ += [ f"{__package__}.tests" ]
