"""
This module contains all tests for the "Scripted Object"
"""

import unittest
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


