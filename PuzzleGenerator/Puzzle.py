# Puzzle.py

import random
import json
import math

from math2d_region import Region, SubRegion
from math2d_planar_graph import PlanarGraph
from math2d_aa_rect import AxisAlignedRectangle
from math2d_vector import Vector
from math2d_affine_transform import AffineTransform

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
            
    def Transform(self, transform):
        self.polygon = transform * self.polygon
        inverse = transform.Inverted()
        for i, symmetry in enumerate(self.symmetry_list):
            self.symmetry_list[i] = transform * symmetry * inverse

class Puzzle(object):
    def __init__(self):
        self.cut_region_list = []
    
    def Name(self):
        return ''
    
    def Generate(self, puzzle_folder):
        
        # Calculate a bounding rectangle for all the cut-regions.
        rect = AxisAlignedRectangle()
        for cut_region in self.cut_region_list:
            rect.GrowFor(cut_region)
        rect.Scale(1.1)

        # Now add the rectangle and the cut-regions to a planar graph.
        graph = PlanarGraph()
        graph.Add(rect)
        for cut_region in self.cut_region_list:
            graph.Add(cut_region)
        
        # Make sure that all cut-regions are tessellated.  This lets us do point tests against the regions.
        for cut_region in self.cut_region_list:
            cut_region.region.Tesselllate()
        
        # Now comes the process of cutting the puzzle.  The only sure algorithm I can think
        # of would use a stabilizer chain to enumerate all elements of the desired group, but
        # that is completely impractical.  The idea here is that if after max_count iteration
        # we have not added any more edges to our graph, then we can be reasonably sure that
        # there are no more cuts to be made.
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
                for point in [edge_segment.point_a, edge_segment.point_b]:
                    if region.ContainsPoint(point) and not region.ContainsPointOnBorder(point):
                        line_segment_list.append(edge_segment)
                        break
            
            # Now let all copied edges undergo a random symmetry of the chosen region, then add them to the graph.
            edge_count_before = len(graph.edge_list)
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
        
        # The desired meshes are now simply all of the empty cycles of the graph.
        polygon_list = graph.GeneratePolygonCycles()
        for polygon in polygon_list:
            polygon.Tessellate()
        
        # Finally, write out the level file along with its accompanying mesh files.
        # Note that I think we can calculate UVs as a function of the object-space coordinates in the shader.
        puzzle_file = puzzle_folder + '/' + 'Puzzle_' + self.Name() + '.json'
        with open(puzzle_file, 'w') as puzzle_handle:
            mesh_list = []
            for i, cut_region in enumerate(self.cut_region_list):
                mesh_file = puzzle_folder + '/Puzzle_' + self.Name() + '_CaptureMesh%d.json' % i, 
                mesh = cut_region.GenerateMesh()
                with open(mesh_file, 'w') as mesh_handle:
                    mesh_handle.write(json.dumps(mesh.Serialize()))
                mesh_list.append({
                    'file': mesh_file,
                    'type': 'capture_mesh',
                    'symmetry_list': [symmetry.Serialize() for symmetry in cut_region.symmetry_list]
                })
            for i, polygon in enumerate(polygon_list):
                mesh_file = puzzle_folder + '/Puzzle_' + self.Name() + '_PictureMesh%d.json' % i,
                with open(mesh_file, 'w') as mesh_handle:
                    mesh_handle.write(json.dumps(polygon.mesh.Serialize()))
                mesh_list.append({
                    'file': mesh_file,
                    'type': 'picture_mesh',
                })
            puzzle_handle.write(json.dumps({
                'mesh_list': mesh_list
            }))