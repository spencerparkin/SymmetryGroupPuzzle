# Render.py

from Math.Interval import CompactInterval
from Math.LineSegment import LineSegment
from Math.Vector import Vector

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
        triangle_data = []
        for vertex in triangle_vertex_stream:
            x = vertex[0]
            y = vertex[1]
            i = int(self.x_interval.LerpValue(x) * float(self.target_image.width))
            j = int(self.y_interval.LerpValue(y) * float(self.target_image.height))
            j = self.target_image.height - j
            i, j = self._ClampCoords(self.target_image, i, j)
            triangle_data.append((float(i), float(j), vertex[2], vertex[3]))
            if len(triangle_data) == 3:
                self._RasterizeTriangle(triangle_data)
                triangle_data = []

    def _ClampCoords(self, image, i, j):
        if i < 0:
            i = 0
        elif i >= image.width:
            i = image.width - 1
        if j < 0:
            j = 0
        elif j >= image.height:
            j = image.height - 1
        return i, j

    def _RasterizeTriangle(self, triangle_data):
        triangle_data.sort(key=lambda vertex: vertex[1])
        line_segment01 = LineSegment(Vector(triangle_data[0][0], triangle_data[0][1]), Vector(triangle_data[1][0], triangle_data[1][1]))
        line_segment02 = LineSegment(Vector(triangle_data[0][0], triangle_data[0][1]), Vector(triangle_data[2][0], triangle_data[2][1]))
        line_segment12 = LineSegment(Vector(triangle_data[1][0], triangle_data[1][1]), Vector(triangle_data[2][0], triangle_data[2][1]))
        line_segment01_uv = LineSegment(Vector(triangle_data[0][2], triangle_data[0][3]), Vector(triangle_data[1][2], triangle_data[1][3]))
        line_segment02_uv = LineSegment(Vector(triangle_data[0][2], triangle_data[0][3]), Vector(triangle_data[2][2], triangle_data[2][3]))
        line_segment12_uv = LineSegment(Vector(triangle_data[1][2], triangle_data[1][3]), Vector(triangle_data[2][2], triangle_data[2][3]))
        smallest_i = float(self.target_image.width)
        largest_i = 0.0
        for vertex in triangle_data:
            if smallest_i > vertex[0]:
                smallest_i = vertex[0]
            if largest_i < vertex[0]:
                largest_i = vertex[0]
        j_start = int(triangle_data[0][1])
        j_stop = int(triangle_data[2][1])
        for j in range(j_start, j_stop):
            line_segment = LineSegment(Vector(smallest_i, float(j)), Vector(largest_i, float(j)))
            if int(triangle_data[0][1]) <= j <= int(triangle_data[1][1]):
                lerp_value01 = line_segment.IntersectWith(line_segment01)[1]
                lerp_value02 = line_segment.IntersectWith(line_segment02)[1]
                scan_line = LineSegment(line_segment01.Lerp(lerp_value01), line_segment02.Lerp(lerp_value02))
                scan_line_uv = LineSegment(line_segment01_uv.Lerp(lerp_value01), line_segment02_uv.Lerp(lerp_value02))
            elif int(triangle_data[1][1]) < j <= int(triangle_data[2][1]):
                lerp_value12 = line_segment.IntersectWith(line_segment12)[1]
                lerp_value02 = line_segment.IntersectWith(line_segment02)[1]
                scan_line = LineSegment(line_segment12.Lerp(lerp_value12), line_segment02.Lerp(lerp_value02))
                scan_line_uv = LineSegment(line_segment12_uv.Lerp(lerp_value12), line_segment02_uv.Lerp(lerp_value02))
            scan_line.pointA.y = float(j)
            scan_line.pointB.y = float(j)
            i_start = min(int(scan_line.pointA.x), int(scan_line.pointB.x))
            i_stop = max(int(scan_line.pointA.x), int(scan_line.pointB.x))
            for i in range(i_start, i_stop + 1):
                point = Vector(float(i), float(j))
                try:
                    lerp_value = scan_line.ContainsPointAt(point)
                except ZeroDivisionError:
                    lerp_value = 0.0
                uv = scan_line_uv.Lerp(lerp_value)
                pixel = self._SampleBaseImageTexture(uv.x, uv.y)
                s = int(point.x)
                t = int(point.y)
                s, t = self._ClampCoords(self.target_image, s, t)
                self.target_image_data[s, t] = pixel

    def _SampleBaseImageTexture(self, u, v):
        i = int(float(self.base_image.width) * u)
        j = int(float(self.base_image.height) * (1.0 - v))
        i, j = self._ClampCoords(self.base_image, i, j)
        pixel = self.base_image_data.getpixel((i, j))
        return pixel