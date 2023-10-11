"""
This module defines the python editor and related classes.

The goal is to eventually expose FreeCAD's python editor, which is currently only available
for C++. So here we have only a very basic substitute with no planes for fancy extensions.

Maybe we'll use other fall backs for earlier FreeCAD versions, like
    https://github.com/mnesarco/FreeCAD_Utils/blob/main/freecad/mnesarco/utils/editor.py
    (GPLv3, i.e. must be installed separately)
or
    https://github.com/pyzo/pyzo/tree/main/pyzo/codeeditor
    (2-clause BSD, i.e. could be embedded)
"""

from PySide import QtGui
from PySide.QtCore import Qt


class FallbackEditor(QtGui.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.setFont(QtGui.QFont("Courier")) # is there some generic monospace font?

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        # some basic auto-indent
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            cursor = self.textCursor()
            previousBlock = cursor.block().previous()
            if previousBlock.isValid():
                line = previousBlock.text()
                indent = line[: len(line) - len(line.lstrip())]
                self.insertPlainText(indent)

        # some basic expand-tabs, using PEP8 recommentation of 4 spaces
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.deletePreviousChar()
            self.insertPlainText(" " * 4)


Editor = FallbackEditor
