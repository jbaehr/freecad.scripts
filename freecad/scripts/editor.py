"""
This module defines the python editor and related classes.

The goal is to eventually expose FreeCAD's python editor, which is currently only available
for C++. So here we have only a very basic substitute with no planes for fancy extensions.

Maybe we'll use other fall backs for earler FC versions, like
    https://github.com/mnesarco/FreeCAD_Utils/blob/main/freecad/mnesarco/utils/editor.py
    (GPLv3, i.e. must be installed separately)
or
    https://github.com/pyzo/pyzo/tree/main/pyzo/codeeditor
    (2-clause BSD, i.e. could be embedded)
"""

from PySide import QtGui


Editor = QtGui.QPlainTextEdit
