"""
This module contains all tests for the "Scripted Object"
"""

import unittest
import tempfile
import pathlib
from math import pi
import FreeCAD

from . import scripted_object


class TestScriptedObject(unittest.TestCase):
    def setUp(self):
        doc_name = self.id().split('.')[-1] # this resuls in the test method name
        self.doc = FreeCAD.newDocument(doc_name)

    def tearDown(self):
        FreeCAD.closeDocument(self.doc.Name)

    def testShapelessObject_Demo(self):
        obj = scripted_object.make_shapeless_object("Demo")
        obj.addProperty("App::PropertyLength", "Hight", "Input")
        obj.addProperty("App::PropertyLength", "Width", "Input")
        obj.addProperty("App::PropertyArea", "Area", "Ouput")
        obj.setPropertyStatus("Area", ["Output", "ReadOnly"])
        obj.Definition = "\n".join([
            "def execute(obj):",
            "   obj.Area = obj.Hight * obj.Width",
            ])
        obj.Hight = "3 mm"
        obj.Width = "2 mm"
        self.doc.recompute()
        self.assertEqual(obj.Area.Value, 6)

    def test3dObject_Demo(self):
        obj = scripted_object.make_3d_object("Demo")
        obj.addProperty("App::PropertyLength", "Radius", "Input")
        obj.Definition = "\n".join([
            "import Part",
            "def execute(obj):",
            "   obj.Shape = Part.makeSphere(obj.Radius)",
            ])
        obj.Radius = "25 mm"
        self.doc.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 4/3 * pi * 25**3, delta=0.1)

    def test2dObject_Demo(self):
        profile = scripted_object.make_2d_object("Demo")
        profile.addProperty("App::PropertyLength", "Radius", "Input")
        profile.Definition = "\n".join([
            "import Part",
            "def execute(obj):",
            "   obj.Shape = Part.makeCircle(obj.Radius)",
            ])
        profile.Radius = "25 mm"
        extrusion = self.doc.addObject("Part::Extrusion", "DemoExtrusion")
        extrusion.Base = profile
        extrusion.LengthFwd = "50 mm"
        extrusion.Solid = True
        self.doc.recompute()
        self.assertAlmostEqual(extrusion.Shape.Volume, pi * 25**2 * 50, delta=0.1)

    def testSecurity_ExecutionWhenLoadingFromDisk_BlockPerDefault(self):
        create_echo_object("Parrot")
        self.doc = save_and_reload(self.doc)
        obj = self.doc.getObject("Parrot")
        obj.In = "hello Polly"
        self.doc.recompute()
        self.assertNotEqual(obj.In, obj.Out)

    def testSecurity_ExecutionWhenLoadingFromDisk_ExecuteWhenExplicitlyAllowed(self):
        create_echo_object("Parrot")
        self.doc = save_and_reload(self.doc)
        obj = self.doc.getObject("Parrot")
        obj.In = "hello Polly"
        obj.AllowExecution = True
        self.doc.recompute()
        self.assertEqual(obj.In, obj.Out)

    def testSecurity_ExecutionWhenLoadingFromDisk_DontSaveAllowFlag(self):
        obj = create_echo_object("Parrot")
        obj.AllowExecution = True
        self.doc = save_and_reload(self.doc)
        obj = self.doc.getObject("Parrot")
        obj.In = "hello Polly"
        self.doc.recompute()
        self.assertNotEqual(obj.In, obj.Out)

    def testSecurity_ExecutionWhenLoadingFromDisk_DontAllowExpressionForAllowence(self):
        obj = create_echo_object("Parrot")
        obj.setExpression("AllowExecution", "True")
        self.doc = save_and_reload(self.doc)
        obj = self.doc.getObject("Parrot")
        obj.In = "hello Polly"
        self.doc.recompute()
        self.assertNotEqual(obj.In, obj.Out)


def save_and_reload(doc):
    """Test helper to save the given doc to disk, reloads and returns it"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = pathlib.Path(tmpdir).joinpath(doc.Name).with_suffix(".FCStd")
        doc.saveAs(str(filename)) # TODO: add pathlib support
        FreeCAD.closeDocument(doc.Name)
        doc = FreeCAD.openDocument(str(filename)) # TODO: add pathlib support
        return doc


def create_echo_object(name):
    """Test helper that creates a scripted object that echos obj.In to obj.Out"""
    obj = scripted_object.make_shapeless_object(name)
    obj.addProperty("App::PropertyString", "In", "Input")
    obj.addProperty("App::PropertyString", "Out", "Ouput")
    obj.setPropertyStatus("Out", ["Output", "ReadOnly"])
    obj.Definition = "def execute(obj): obj.Out = obj.In"
    return obj
