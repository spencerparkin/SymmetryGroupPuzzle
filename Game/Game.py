# Game.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from Math.Rectangle import Rectangle
from Math.Vector import Vector
from Puzzle.Level import MakePuzzle
from Puzzle.Texture import Texture

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Symmetry Group Puzzle')
        self.context = None
        self.level = 1
        self.puzzle = MakePuzzle(self.level)
        self.texture = Texture(r'C:\SymmetryGroupPuzzle\Images\image0.png')

    def initializeGL(self):
        #self.context = QtGui.QOpenGLContext(self)
        #format = QtGui.QSurfaceFormat()
        #self.context.setFormat(format)
        #self.context.create()
        #self.context.makeCurrent(self)

        glShadeModel(GL_SMOOTH)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.7, 0.7, 0.7, 0.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        screen_rectangle = Rectangle(Vector(0.0, 0.0), Vector(float(width), float(height)))
        adjusted_window = self.puzzle.window.Clone()
        adjusted_window.ContractToMatchAspectRatioOf(screen_rectangle)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(adjusted_window.min_point.x,
                   adjusted_window.max_point.x,
                   adjusted_window.min_point.y,
                   adjusted_window.max_point.y)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.texture.Bind()
        glBegin(GL_QUADS)
        try:
            glTexCoord2f(0.0, 0.0)
            glVertex2f(self.puzzle.window.min_point.x, self.puzzle.window.min_point.y)
            glTexCoord2f(1.0, 0.0)
            glVertex2f(self.puzzle.window.max_point.x, self.puzzle.window.min_point.y)
            glTexCoord2f(1.0, 1.0)
            glVertex2f(self.puzzle.window.max_point.x, self.puzzle.window.max_point.y)
            glTexCoord2f(0.0, 1.0)
            glVertex2f(self.puzzle.window.min_point.x, self.puzzle.window.max_point.y)
        finally:
            glEnd()

        # I'm almost certain that I'm not mis-using OpenGL here, but these lines,
        # uncommented, cause some undesirable behavior that I think is a bug with
        # however OpenGL is bound in Python.  What a pain in the ass.  I've never
        # seen such crappy behavior like this while writing a C++/OpenGL application,
        # of which I've written about a billion.  Python with OpenGL sucks like crap.
        # Maybe I'm just not setting it up all correctly?  I don't know.
        #glDisable(GL_TEXTURE_2D)
        #self.puzzle.RenderShadow()

        self.texture.Bind()
        self.puzzle.RenderShapes()

        glFlush()

    def resizeGL(self, width, height):
        pass # glViewport(0, 0, width, height)

    def mousePressEvent(self, event):
        pass

    # TODO: Highlight nearest cutter to mouse at all times.
    #       Use mouse wheel for rotations; clicks for reflections.

    # TODO: Let them choose any picture for any puzzle.
    #       Let them skip any level and go to the next.

    # TODO: Support puzzle saving and loading.  The puzzle object
    #       should serialize and deserialize to/from JSON.

def ExceptionHook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = ExceptionHook
    app = QtGui.QGuiApplication(sys.argv)
    win = Window()
    win.resize(640, 480)
    win.show()
    ret_code = app.exec_()
    sys.exit(ret_code)