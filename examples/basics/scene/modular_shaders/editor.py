# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
# QScintilla editor
#
# Adapted from Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#
# API: http://pyqt.sourceforge.net/Docs/QScintilla2/classQsciScintilla.html
#
"""

import sys
import re
from PyQt5.QtCore import *  # noqa
from PyQt5.QtWidgets import *  # noqa


try:
    from PyQt5 import Qsci
    from PyQt5.Qsci import QsciScintilla
    HAVE_QSCI = True
except ImportError:
    HAVE_QSCI = False

if not HAVE_QSCI:
    # backup editor in case QScintilla is not available
    class Editor(QPlainTextEdit):
        def __init__(self, parent=None, language=None):
            QPlainTextEdit.__init__(self, parent)

        def setText(self, text):
            self.setPlainText(text)

        def text(self):
            return str(self.toPlainText()).encode('UTF-8')

        def __getattr__(self, name):
            return lambda: None

else:
    class Editor(QsciScintilla):
        ARROW_MARKER_NUM = 8

        def __init__(self, parent=None, language='Python'):
            super(Editor, self).__init__(parent)
            self.setIndentationsUseTabs(False)
            self.setIndentationWidth(4)

            # Set the default font
            font = QFont()
            font.setFamily('DejaVu Sans Mono')
            font.setFixedPitch(True)
            font.setPointSize(10)
            self.setFont(font)
            self.setMarginsFont(font)
            self.zoomIn()

            # Margin 0 is used for line numbers
            fontmetrics = QFontMetrics(font)
            self.setMarginsFont(font)
            self.setMarginWidth(0, fontmetrics.width("000") + 6)
            self.setMarginLineNumbers(0, True)
            self.setMarginsBackgroundColor(QColor("#cccccc"))

            self._marker = None
            # Clickable margin 1 for showing markers
            # self.setMarginSensitivity(1, True)
            # self.connect(self,
            #    SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'),
            #    self.on_margin_clicked)
            self.markerDefine(QsciScintilla.RightArrow, self.ARROW_MARKER_NUM)
            self.setMarkerBackgroundColor(QColor("#ee1111"),
                                          self.ARROW_MARKER_NUM)

            # Brace matching: enable for a brace immediately before or after
            # the current position
            #
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

            # Current line visible with special background color
            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

            # Set Python lexer
            # Set style for Python comments (style number 1) to a fixed-width
            # courier.
            #
            lexer = getattr(Qsci, 'QsciLexer' + language)()
            lexer.setDefaultFont(font)
            self.setLexer(lexer)
            self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

            # Don't want to see the horizontal scrollbar at all
            # Use raw message to Scintilla here (all messages are documented
            # here: http://www.scintilla.org/ScintillaDoc.html)
            self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

            self.setWrapMode(QsciScintilla.WrapWord)

            self.setEolMode(QsciScintilla.EolUnix)
            # not too small
            # self.setMinimumSize(600, 450)

        def set_marker(self, line):
            self.clear_marker()
            self.markerAdd(line, self.ARROW_MARKER_NUM)
            self._marker = line

        def clear_marker(self):
            if self._marker is not None:
                self.markerDelete(self._marker, self.ARROW_MARKER_NUM)

        # def on_margin_clicked(self, nmargin, nline, modifiers):
            # Toggle marker for the line the margin was clicked on
            # if self.markersAtLine(nline) != 0:
                # self.markerDelete(nline, self.ARROW_MARKER_NUM)
            # else:
                # self.markerAdd(nline, self.ARROW_MARKER_NUM)

        def wheelEvent(self, ev):
            # Use ctrl+wheel to zoom in/out
            if Qt.ControlModifier & ev.modifiers():
                if ev.delta() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()
            else:
                return super(Editor, self).wheelEvent(ev)

        def keyPressEvent(self, ev):
            if int(Qt.ControlModifier & ev.modifiers()) > 0:
                if ev.key() == Qt.Key_Slash:
                    self.comment(True)
                    return
                elif ev.key() == Qt.Key_Question:
                    self.comment(False)
                    return
                elif (ev.key() == Qt.Key_Z and
                      Qt.ShiftModifier & ev.modifiers()):
                    self.redo()
                    return
                elif ev.key() == Qt.Key_Q:
                    sys.exit(0)
            return super(Editor, self).keyPressEvent(ev)

        def text(self):
            return str(super(Editor, self).text()).encode('UTF-8')

        def comment(self, comment=True):
            sel = self.getSelection()[:]
            text = self.text()
            lines = text.split('\n')
            if sel[0] == -1:
                # toggle for just this line
                row, col = self.getCursorPosition()
                line = lines[row]
                self.setSelection(row, 0, row, len(line))
                if comment:
                    line = '#' + line
                else:
                    line = line.replace("#", "", 1)
                self.replaceSelectedText(line)
                self.setCursorPosition(row, col+(1 if col > 0 else 0))
            else:
                block = lines[sel[0]:sel[2]]
                # make sure all lines have #
                new = []
                if comment:
                    for line in block:
                        new.append('#' + line)
                else:
                    for line in block:
                        if line.strip() == '':
                            new.append(line)
                            continue
                        if re.match(r'\s*\#', line) is None:
                            return
                        new.append(line.replace('#', '', 1))
                self.setSelection(sel[0], 0, sel[2], 0)
                self.replaceSelectedText('\n'.join(new) + '\n')
                # shift = 1 if comment else -1
                self.setSelection(sel[0], max(0, sel[1]), sel[2], sel[3])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = Editor()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    editor.resize(800, 800)
    app.exec_()
