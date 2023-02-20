"""
This module contains all tests for the "Scripted Object"
"""

import unittest
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


