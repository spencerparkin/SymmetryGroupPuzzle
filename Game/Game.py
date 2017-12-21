# Game.py

import sys
import math
import random
import traceback

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from Math.Polygon import Polygon
from Math.Vector import Vector

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Symmetry Group Puzzle')
        self.context = None
        self.polygon = Polygon([
            Vector(-4.0, -4.0),
            Vector(4.0, -4.0),
            Vector(4.0, 4.0),
            Vector(3.0, 4.0),
            Vector(3.0, 0.0),
            Vector(2.0, 0.0),
            Vector(-4.0, 4.0)
        ])

    def initializeGL(self):
        self.context = QtGui.QOpenGLContext(self)
        format = QtGui.QSurfaceFormat()
        self.context.setFormat(format)
        self.context.create()
        self.context.makeCurrent(self)

        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.7, 0.7, 0.7, 0.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        aspectRatio = float(width) / float(height)
        length = 5.0

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if aspectRatio > 1.0:
            glOrtho(-length * aspectRatio, length * aspectRatio, -length, length, -1.0, 100.0)
        else:
            glOrtho(-length, length, -length / aspectRatio, length / aspectRatio, -1.0, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        glBegin(GL_TRIANGLES)
        try:
            for triangle in self.polygon.triangle_list:
                r = float(random.randint(0, 255)) / 255.0
                g = float(random.randint(0, 255)) / 255.0
                b = float(random.randint(0, 255)) / 255.0
                glColor3f(r, g, b)
                for i in range(3):
                    point = triangle.vertex_list[i]
                    glVertex2f(point.x, point.y)
        finally:
            glEnd()

        glFlush()

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            self.polygon.Tessellate()
            self.update()

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