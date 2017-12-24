# Texture.py

from OpenGL.GL import *
from PyQt5 import QtGui

class Texture(object):
    def __init__(self, texture_image_file):
        self.texture_image_file = texture_image_file
        self.texture_object = None

    def Bind(self):
        glEnable(GL_TEXTURE_2D)
        if self.texture_object is not None:
            glBindTexture(GL_TEXTURE_2D, self.texture_object)
        else:
            image = QtGui.QImage()
            if not image.load(self.texture_image_file):
                raise Exception('Failed to load textures: ' + self.texture_image_file)
            format = image.format()
            if format != QtGui.QImage.Format_RGB32:
                image = image.convertToFormat(QtGui.QImage.Format_RGB32)

            width = image.width()
            height = image.height()

            pixel_data = []
            for j in range(height):
                for i in range(width):
                    pixel = image.pixel(i, height - 1 - j)
                    r = (pixel & 0x00FF0000) >> 16
                    g = (pixel & 0x0000FF00) >> 8
                    b = (pixel & 0x000000FF) >> 0
                    pixel_data += [r, g, b]
            pixel_data = bytes(pixel_data)

            self.texture_object = glGenTextures(1)

            glBindTexture(GL_TEXTURE_2D, self.texture_object)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixel_data)