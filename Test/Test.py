# Test.py

# Here we test various algorithms and data-structures to be used in the app.
# It is a means to an end, not an end in and of itself.

import sys
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from Math.Polygon import Polygon
from Math.Vector import Vector
from Math.LineSegment import LineSegment
from Math.Transform import AffineTransform

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context = None
        self.polygonA = Polygon([Vector(-2.0, -2.0), Vector(2.0, -2.0), Vector(2.0, 2.0), Vector(-2.0, 2.0)])
        self.polygonB = Polygon([Vector(-2.0, -2.0), Vector(4.0, -2.0), Vector(4.0, 4.0), Vector(-2.0, 4.0)])
        self.polygon_list = None
        self.edge_list = None

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

        try:
            if self.edge_list:
                for edge in self.edge_list:
                    if edge[1] == 0:
                        glColor3f(1.0, 1.0, 1.0)
                    else:
                        glColor3f(1.0, 0.0, 0.0)
                    self.DrawArrow(edge[0])
            elif self.polygon_list:
                glColor3f(1.0, 1.0, 1.0)
                for polygon in self.polygon_list:
                    self.DrawPolygon(polygon)
            else:
                glColor3f(1.0, 0.0, 0.0)
                self.DrawPolygon(self.polygonA)
                glColor3f(0.0, 0.0, 1.0)
                self.DrawPolygon(self.polygonB)
        except Exception as ex:
            print('Exception: ' + str(ex))

        glFlush()

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            # TODO: Test tessellation algorithm.
            self.polygon_list = self.polygonA.Cut(self.polygonB)
            self.update()

    def DrawPolygon(self, polygon):
        edge_list = polygon.EdgeList()
        for edge in edge_list:
            self.DrawArrow(edge)

    def DrawArrow(self, line_segment):
        glBegin(GL_LINES)
        glVertex2f(line_segment.pointA.x, line_segment.pointA.y)
        glVertex2f(line_segment.pointB.x, line_segment.pointB.y)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        try:
            glVertex2f(line_segment.pointB.x, line_segment.pointB.y)
            affine_transform = AffineTransform()
            affine_transform.linear_transform.xAxis = (line_segment.pointB - line_segment.pointA).Normalized()
            affine_transform.linear_transform.yAxis = affine_transform.linear_transform.xAxis.Rotated(math.pi / 2.0)
            affine_transform.translation = line_segment.pointB
            count = 10
            radius = line_segment.Length() / 20.0
            for i in range(count + 1):
                angle = 3.0 * math.pi / 4.0 + (float(i) / float(count)) * math.pi / 2.0
                vector = Vector(radius * math.cos(angle), radius * math.sin(angle))
                point = affine_transform.Transform(vector)
                glVertex2f(point.x, point.y)
        finally:
            glEnd()

if __name__ == '__main__':
    app = QtGui.QGuiApplication(sys.argv)
    win = Window()
    win.resize(640, 480)
    win.show()
    app.exec_()