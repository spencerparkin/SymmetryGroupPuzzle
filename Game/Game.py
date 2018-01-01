# Game.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from Math.Rectangle import Rectangle
from Math.Vector import Vector
from Math.LineSegment import LineSegment
from Puzzle.Level import MakePuzzle
from Puzzle.Texture import Texture

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Symmetry Group Puzzle')
        self.context = None
        self.level = 1
        self.puzzle = MakePuzzle(self.level)
        self.texture = Texture('Images/image1.png')
        self.adjusted_window = None
        self.nearest_cutter = None
        self.nearest_axis = None

    def initializeGL(self):
        #self.context = QtGui.QOpenGLContext(self)
        #format = QtGui.QSurfaceFormat()
        #self.context.setFormat(format)
        #self.context.create()
        #self.context.makeCurrent(self)

        glShadeModel(GL_SMOOTH)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.7, 0.7, 0.7, 0.0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        screen_rectangle = Rectangle(Vector(0.0, 0.0), Vector(float(width), float(height)))
        self.adjusted_window = self.puzzle.window.Clone()
        self.adjusted_window.ContractToMatchAspectRatioOf(screen_rectangle)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.adjusted_window.min_point.x,
                   self.adjusted_window.max_point.x,
                   self.adjusted_window.min_point.y,
                   self.adjusted_window.max_point.y)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

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

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)

        self.puzzle.RenderShadow()

        glEnable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

        self.texture.Bind()
        self.puzzle.RenderShapes()

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)

        if self.nearest_cutter is not None:
            cutter = self.puzzle.cutter_list[self.nearest_cutter]
            glColor4f(1.0, 1.0, 1.0, 0.1)
            glLineWidth(4.0)
            cutter.RenderOutline()
            if self.nearest_axis is not None:
                axis = cutter.axes_of_symmetry[self.nearest_axis]
                radius = cutter.polygon.AverageRadius() * 2.0
                pointA = Vector().Lerp(cutter.center, cutter.center + axis, radius)
                pointB = Vector().Lerp(cutter.center, cutter.center - axis, radius)
                glBegin(GL_LINES)
                glVertex2f(pointA.x, pointA.y)
                glVertex2f(pointB.x, pointB.y)
                glEnd()

        glFlush()

    def resizeGL(self, width, height):
        pass # glViewport(0, 0, width, height)

    def mouseMoveEvent(self, event):
        if self.adjusted_window is not None:
            rectangle = Rectangle(Vector(0.0, 0.0), Vector(float(self.width()), float(self.height())))
            point = Vector(float(event.x()), float(event.y()))
            point = rectangle.Map(point, self.adjusted_window)
            point.y = -point.y
            self.nearest_cutter = self.puzzle.NearestCutter(point)
            self.nearest_axis = self.puzzle.NearestAxisOfSymmetry(point)
            self.update()

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            if self.nearest_cutter is not None and self.nearest_axis is not None:
                self.puzzle.ReflectCutter(self.nearest_cutter, self.nearest_axis)
                self.update()

    def wheelEvent(self, event):
        if self.nearest_cutter is not None:
            angleDelta = event.angleDelta().y()
            steps = angleDelta / 120
            while steps > 0:
                self.puzzle.RotateCutter(self.nearest_cutter, False)
                steps -= 1
            while steps < 0:
                self.puzzle.RotateCutter(self.nearest_cutter, True)
                steps += 1
            self.update()

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