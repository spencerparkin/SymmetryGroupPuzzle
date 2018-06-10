# Puzzle.py

import sys
import random
import json
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from math2d_region import Region, SubRegion
from math2d_planar_graph import PlanarGraph
from math2d_aa_rect import AxisAlignedRectangle
from math2d_vector import Vector
from math2d_affine_transform import AffineTransform
from math2d_linear_transform import LinearTransform
from math2d_line_segment import LineSegment

class CutRegion(object):
    def __init__(self):
        self.region = None
        # We don't need every symmetry of the shape here.  We only need enough
        # to generate the symmetry group of the shape.  We add a bit more symmetries
        # than that, however, to make things convenient for the user.
        self.symmetry_list = []
    
    def GenerateRegularPolygon(self, sides, radius):
        sub_region = SubRegion()
        sub_region.polygon.MakeRegularPolygon(sides, radius)
        self.region = Region()
        self.region.sub_region_list.append(sub_region)
        for i in range(3):
            vector = Vector(angle=2.0 * math.pi * float(i) / float(sides))
            symmetry = AffineTransform()
            symmetry.linear_transform.Reflection(vector)
            self.symmetry_list.append(symmetry)
        symmetry = AffineTransform()
        symmetry.linear_transform.Rotation(2.0 * math.pi / float(sides))
        self.symmetry_list.append(symmetry)
        symmetry = AffineTransform()
        symmetry.linear_transform.Rotation(-2.0 * math.pi / float(sides))
        self.symmetry_list.append(symmetry)

    def GenerateRectangle(self, width, height):
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-width / 2.0, -height / 2.0))
        sub_region.polygon.vertex_list.append(Vector(width / 2.0, -height / 2.0))
        sub_region.polygon.vertex_list.append(Vector(width / 2.0, height / 2.0))
        sub_region.polygon.vertex_list.append(Vector(-width / 2.0, height / 2.0))
        self.region = Region()
        self.region.sub_region_list.append(sub_region)
        symmetry = AffineTransform()
        symmetry.linear_transform.Reflection(Vector(1.0, 0.0))
        self.symmetry_list.append(symmetry)
        symmetry = AffineTransform()
        symmetry.linear_transform.Reflection(Vector(0.0, 1.0))
        self.symmetry_list.append(symmetry)
        symmetry = AffineTransform()
        symmetry.linear_transform.Rotation(math.pi)
        self.symmetry_list.append(symmetry)

    def Transform(self, transform):
        self.region = transform * self.region
        inverse = transform.Inverted()
        for i, symmetry in enumerate(self.symmetry_list):
            self.symmetry_list[i] = transform * symmetry * inverse

class Puzzle(object):
    def __init__(self):
        self.cut_region_list = []
    
    def Name(self):
        return ''
    
    def Generate(self, puzzle_folder):
        
        # Add the cut-regions to a planar graph.
        print('Adding cut regions...')
        graph = PlanarGraph()
        for cut_region in self.cut_region_list:
            graph.Add(cut_region.region)
        
        # For debugging purposes...
        #DebugDraw(graph)
        
        # Make sure that all cut-regions are tessellated.  This lets us do point tests against the regions.
        print('Tessellating cut regions...')
        for cut_region in self.cut_region_list:
            cut_region.region.Tessellate()
        
        # Now comes the process of cutting the puzzle.  The only sure algorithm I can think
        # of would use a stabilizer chain to enumerate all elements of the desired group, but
        # that is completely impractical.  The idea here is that if after max_count iteration
        # we have not added any more edges to our graph, then we can be reasonably sure that
        # there are no more cuts to be made.
        print('Generating cuts...')
        random.seed(0)
        max_count = 20
        count = 0
        while count < max_count:
            
            # Copy all edges of the graph contained in and not on the border of a randomly chosen region.
            i = random.randint(0, len(self.cut_region_list) - 1)
            cut_region = self.cut_region_list[i]
            region = cut_region.region
            line_segment_list = []
            for edge in graph.edge_list:
                edge_segment = graph.EdgeSegment(edge)
                for point in [edge_segment.point_a, edge_segment.point_b, edge_segment.Lerp(0.5)]:
                    if region.ContainsPoint(point) and not region.ContainsPointOnBorder(point):
                        line_segment_list.append(edge_segment)
                        break

            # Now let all copied edges, if any, undergo a random symmetry of the chosen region, then add them to the graph.
            edge_count_before = len(graph.edge_list)
            if len(line_segment_list) > 0:
                i = random.randint(0, len(cut_region.symmetry_list) - 1)
                symmetry = cut_region.symmetry_list[i]
                for line_segment in line_segment_list:
                    line_segment = symmetry * line_segment
                    graph.Add(line_segment)
            edge_count_after = len(graph.edge_list)
            
            # Count how long we've gone without adding any new edges.
            added_edge_count = edge_count_after - edge_count_before
            if added_edge_count > 0:
                count = 0
            else:
                count += 1

        # For debugging purposes...
        #DebugDraw(graph)

        # Calculate a bounding rectangle for the graph, size it up a bit, then add it to the graph.
        print('Adding border...')
        rect = AxisAlignedRectangle()
        rect.GrowFor(graph)
        rect.Scale(1.1)
        graph.Add(rect)

        # Before we can pull the empty cycles out of the graph, we need to merge all connected components into one.
        print('Coalescing all connected components...')
        while True:
            sub_graph_list, dsf_set_list = graph.GenerateConnectedComponents()
            if len(sub_graph_list) == 1:
                break
            smallest_distance = None
            line_segment = None
            for i in range(len(graph.vertex_list)):
                dsf_set_a = dsf_set_list[i]
                for j in range(i + 1, len(graph.vertex_list)):
                    dsf_set_b = dsf_set_list[j]
                    if dsf_set_a != dsf_set_b:
                        distance = (graph.vertex_list[i] - graph.vertex_list[j]).Length()
                        if smallest_distance is None or distance < smallest_distance:
                            smallest_distance = distance
                            line_segment = LineSegment(graph.vertex_list[i], graph.vertex_list[j])
            graph.Add(line_segment)

        # For debugging purposes...
        #DebugDraw(graph)

        # The desired meshes are now simply all of the empty cycles of the graph.
        print('Reading all empty cycles...')
        polygon_list = graph.GeneratePolygonCycles()
        for polygon in polygon_list:
            polygon.Tessellate()
        
        # For debugging purposes...
        #mesh_list = [polygon.mesh for polygon in polygon_list]
        #DebugDraw(mesh_list)
        
        # Finally, write out the level file along with its accompanying mesh files.
        # Note that I think we can calculate UVs as a function of the object-space coordinates in the shader.
        print('Writing level files...')
        mesh_list = []
        for i, cut_region in enumerate(self.cut_region_list):
            mesh_file = 'Puzzle_' + self.Name() + '_CaptureMesh%d.json' % i
            mesh = cut_region.region.GenerateMesh()
            with open(puzzle_folder + '/' + mesh_file, 'w') as mesh_handle:
                mesh_handle.write(json.dumps(mesh.Serialize(), sort_keys=True, indent=4, separators=(',', ': ')))
            mesh_list.append({
                'file': mesh_file,
                'type': 'capture_mesh',
                'symmetry_list': [symmetry.Serialize() for symmetry in cut_region.symmetry_list]
                # TODO: We need to add some hot-spot data here to aide in knowing which symmetry to use based on mouse location.
            })
        for i, polygon in enumerate(polygon_list):
            mesh_file = 'Puzzle_' + self.Name() + '_PictureMesh%d.json' % i
            with open(puzzle_folder + '/' + mesh_file, 'w') as mesh_handle:
                mesh_handle.write(json.dumps(polygon.mesh.Serialize(), sort_keys=True, indent=4, separators=(',', ': ')))
            mesh_list.append({
                'file': mesh_file,
                'type': 'picture_mesh',
            })
        puzzle_file = 'Puzzle_' + self.Name() + '.json'
        with open(puzzle_folder + '/' + puzzle_file, 'w') as puzzle_handle:
            puzzle_handle.write(json.dumps({
                'mesh_list': mesh_list,
                'window': rect.Serialize()
            }, sort_keys=True, indent=4, separators=(',', ': ')))

class DebugWindow(QtGui.QOpenGLWindow):
    def __init__(self, parent=None, object=None):
        super().__init__(parent)
        self.object = object

    def initializeGL(self):
        glShadeModel(GL_FLAT)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

        aspect_ratio = float(width) / float(height)
        extent = 6.0

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if aspect_ratio > 0.0:
            gluOrtho2D(-extent * aspect_ratio, extent * aspect_ratio, -extent, extent)
        else:
            gluOrtho2D(-extent, extent, -extent / aspect_ratio, extent / aspect_ratio)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if self.object is not None:
            if type(self.object) is list:
                for sub_object in self.object:
                    r = random.uniform(0.0, 1.0)
                    g = random.uniform(0.0, 1.0)
                    b = random.uniform(0.0, 1.0)
                    glColor3f(r, g, b)
                    sub_object.Render()
            else:
                self.object.Render()

        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

def DebugDraw(object):
    app = QtGui.QGuiApplication(sys.argv)
    
    win = DebugWindow(None, object)
    win.resize(640, 480)
    win.show()
    
    result = app.exec_()
    return result