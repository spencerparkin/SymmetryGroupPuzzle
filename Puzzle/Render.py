# Render.py

from Math.Interval import CompactInterval

class Renderer(object):
    def __init__(self, base_image, base_image_data, target_image, target_image_data):
        self.base_image = base_image
        self.base_image_data = base_image_data
        self.target_image = target_image
        self.target_image_data = target_image_data
        self.x_interval = CompactInterval()
        self.y_interval = CompactInterval()

    def SetPlaneWindow(self, x_min, x_max, y_min, y_max):
        self.x_interval.min_point = x_min
        self.x_interval.max_point = x_max
        self.y_interval.min_point = y_min
        self.y_interval.max_point = y_max

    def RasterizeTriangles(self, triangle_vertex_stream):
        for vertex in triangle_vertex_stream:
            x = vertex[0]
            y = vertex[1]
            i = int(self.x_interval.LerpValue(x) * float(self.target_image.width))
            j = int(self.y_interval.LerpValue(y) * float(self.target_image.height))
            j = self.target_image.height - j
            i, j = self._ClampCoords(self.target_image, i, j)
            vertex[0] = i
            vertex[1] = j
        for i in range(0, len(triangle_vertex_stream), 3):
            self._RasterizeTriangle(triangle_vertex_stream[i:i+3])

    def _ClampCoords(self, image, i, j):
        if i < 0:
            i = 0
        elif i > image.width:
            i = image.width
        if j < 0:
            j = 0
        elif j > image.height:
            j = image.height
        return i, j

    def _RasterizeTriangle(self, triangle_data):
        pass # Use x_interval.Lerp() and .LerpValue() here...

    def _SampleBaseImageTexture(self, u, v):
        i = int(float(self.base_image.width) * u)
        j = int(float(self.base_image.height) * (1.0 - v))
        i, j = self._ClampCoords(self.base_image, i, j)
        pixel = self.base_image_data.getpixel(i, j)
        return pixel