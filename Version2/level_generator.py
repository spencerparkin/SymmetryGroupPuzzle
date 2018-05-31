# level_generator.py

# This file generates all the level files that get served to the client.

import math
import cmath
import copy
import json
import argparse

def Cross(vector_a, vector_b):
    return vector_a.real * vector_b.imag - vector_a.imag * vector_b.real

def Dot(vector_a, vector_b):
    return vector_a.real * vector_b.real + vector_a.imag * vector_b.imag

def Project(vector, normal):
    return Dot(vector, normal) * normal

def Reject(vector, normal):
    return vector - Project(vector, normal)

def Reflect(vector, normal):
    return Project(vector, normal) - Reject(vector, normal)

def Rotate(vector, angle):
    return vector * cmath.exp(complex(0.0, angle))

class Shape(object):
    def __init__(self):
        self.point_list = []
        self.triangle_list = [] # These must be wound CCW in the plane.
        # There might be a way to calculate the symmetries of the shape
        # as a function of the shape itself, but until I can figure that
        # out, the symmetries will be computed with fore-knowledge of the shape.
        # Not all rotation symmetries need appear in this list.  We only need
        # enough of them to generate the group of symmetries of the shape.
        self.symmetry_list = []

    def ContainsPoint(self, point):
        for triangle in self.triangle_list:
            for i in range(3):
                j = (i + 1) % 3
                vector_a = self.point_list[triangle[i]] - point
                vector_b = self.point_list[triangle[j]] - point
                det = Cross(vector_a, vector_b)
                if det < 0.0:
                    break
            else:
                return True
        return False

    def Transform(self, transform):
        # If there is any shear in the given transform, then not all
        # symmetries of the shape are necessarily preserved here.
        for i, point in enumerate(self.point_list):
            point = transform.Transform(point)
            self.point_list[i] = point
        inverse = transform.Copy()
        inverse.Invert()
        for i, symmetry in enumerate(self.symmetry_list):
            symmetry = inverse * symmetry * transform
            self.symmetry_list[i] = symmetry

    def MakeRegularPolygon(self, radius, sides):
        self.point_list = []
        self.triangle_list = []
        for i in range(sides):
            angle = 2.0 * math.pi * float(i) / float(sides)
            normal = cmath.exp(complex(0.0, angle))
            self.point_list.append(radius * normal)
            self.symmetry_list.append(AffineTransform().MakeReflection(normal))
        self.point_list.append(complex(0.0, 0.0))
        for i in range(sides):
            j = (i + 1) % sides
            self.triangle_list.append((i, j, sides))
        self.symmetry_list.append(AffineTransform().MakeRotation(2.0 * math.pi / float(sides)))
        return self

    # TODO: There are other interesting kinds of shapes we can make.
    #       They can be of all sorts of topologies.

class Window(object):
    def __init__(self, min_point, max_point):
        self.min_point = min_point
        self.max_point = max_point

    def Map(self, point, window):
        u = (point.real - window.min_point.real) / (window.max_point.real - window.min_point.real)
        v = (point.imag - window.min_point.imag) / (window.max_point.imag - window.min_point.imag)
        point = complex(
            self.min_point.real + u * (self.max_point.real - self.min_point.real),
            self.min_point.imag + v * (self.max_point.imag - self.min_point.imag)
        )
        return point

class AffineTransform(object):
    def __init__(self):
        self.MakeIdentity()

    def Copy(self):
        return copy.deepcopy(self)

    def Transform(self, point, apply_translation=True):
        point = self.x_axis * point.real + self.y_axis * point.imag
        if apply_translation:
            point += self.translation
        return point

    def Concatinate(self, transform):
        self.x_axis = transform.Transform(self.x_axis, False)
        self.y_axis = transform.Transform(self.y_axis, False)
        self.translation = transform.Transform(self.translation)
        return self

    def __mul__(self, other):
        return AffineTransform().Concatinate(self).Concatinate(other)

    def Determinant(self):
        return Cross(self.x_axis, self.y_axis)

    def Invert(self):
        try:
            x_axis = complex(self.y_axis.imag, -self.x_axis.imag)
            y_axis = complex(-self.y_axis.real, self.x_axis.real)
            det = self.Determinant()
            self.x_axis = x_axis / det
            self.y_axis = y_axis / det
        except ZeroDivisionError:
            return False

    def MakeIdentity(self):
        self.x_axis = complex(1.0, 0.0)
        self.y_axis = complex(0.0, 1.0)
        self.translation = complex(0.0, 0.0)
        return self

    def MakeTranslation(self, translation):
        self.MakeIdentity()
        self.translation = translation
        return self

    def MakeReflection(self, normal):
        self.MakeIdentity()
        self.x_axis = Reflect(self.x_axis, normal)
        self.y_axis = Reflect(self.y_axis, normal)
        return self

    def MakeRotation(self, angle):
        self.MakeIdentity()
        self.x_axis = Rotate(self.x_axis, angle)
        self.y_axis = Rotate(self.y_axis, angle)
        return self

    def MakeReflectionAboutPoint(self, point, normal):
        self.MakeIdentity()
        self.Concatinate(AffineTransform().MakeTranslation(-point))
        self.Concatinate(AffineTransform().MakeReflection(normal))
        self.Concatinate(AffineTransform().MakeTranslation(point))
        return self

    def MakeRotationAboutPoint(self, point, angle):
        self.MakeIdentity()
        self.Concatinate(AffineTransform().MakeTranslation(-point))
        self.Concatinate(AffineTransform().MakeRotation(angle))
        self.Concatinate(AffineTransform().MakeTranslation(point))
        return self

    def MakeScale(self, scale):
        self.MakeIdentity()
        self.x_axis *= scale
        self.y_axis *= scale
        return self

class ImagePermutation(object):
    def __init__(self, width, height):
        self.map = [[(i, j) for j in range(width)] for i in range(height)]
        self.width = width
        self.height = height

    def IterateCoordsNear(self, coords):
        coords_list = []
        for i in range(-10, 10):
            for j in range(-10, 10):
                coords_list.append((coords[0] + i, coords[1] + j))
        coords_list.sort(key=lambda other_coords: (other_coords[0] - coords[0])**2 + (other_coords[1] - coords[1])**2)
        for other_coords in coords_list:
            if 0 <= other_coords[0] < self.width and 0 <= other_coords[1] < self.height: 
                yield other_coords

    def Generate(self, world_window, shape, symmetry):
        hit_set = set()
        image_window = Window(complex(0.0, 0.0), complex(float(self.width - 1), float(self.height - 1)))
        for i in range(self.width):
            for j in range(self.height):
                coords = self.map[i][j]
                image_point = complex(float(coords[0]), float(coords[1]))
                world_point = world_window.Map(image_point, image_window)
                if not shape.ContainsPoint(world_point):
                    hit_set.add(coords)
        for i in range(self.width):
            for j in range(self.height):
                coords = self.map[i][j]
                image_point = complex(float(coords[0]), float(coords[1]))
                world_point = world_window.Map(image_point, image_window)
                if shape.ContainsPoint(world_point):
                    world_point = symmetry.Transform(world_point)
                    image_point = image_window.Map(world_point, world_window)
                    coords = (int(round(image_point.real)), int(round(image_point.imag)))
                    if coords in hit_set:
                        for other_coords in self.IterateCoordsNear(coords): 
                            if other_coords not in hit_set:
                                coords = other_coords
                                break
                        else:
                            raise Exception('Could not find coords for permutation mapping.')
                    self.map[i][j] = coords
                    hit_set.add(coords)

    def IsValid(self):
        count_matrix = [[0 for j in range(self.width)] for i in range(self.height)]
        for i in range(self.width):
            for j in range(self.height):
                coords = self.map[i][j]
                count_matrix[coords[0]][coords[1]] += 1
        for i in range(self.width):
            for j in range(self.height):
                coords = self.map[i][j]
                if count_matrix[coords[0]][coords[1]] != 1:
                    return False
        return True

class LevelBase(object):
    def __init__(self):
        pass

    def MakeWindow(self):
        raise Exception('Pure virtual call.')

    def MakeShapes(self):
        raise Exception('Pure virtual call.')

class Level_1(LevelBase):
    def __init__(self):
        super().__init__()

    def MakeWindow(self):
        return Window(complex(-10.0, -10.0), complex(10.0, 10.0))

    def MakeShapes(self):
        shape_list = []

        #transform = AffineTransform()
        #transform.MakeScale(4.0)
        #transform.Concatinate(AffineTransform().MakeTranslation(complex(-2.0, 0.0)))
        shape = Shape().MakeRegularPolygon(1.0, 3)
        #shape.Transform(transform)
        shape_list.append(shape)

        '''transform = AffineTransform()
        transform.MakeScale(4.0)
        transform.Concatinate(AffineTransform().MakeRotation(math.pi / 3.0))
        transform.Concatinate(AffineTransform().MakeTranslation(complex(2.0, 0.0)))
        shape = Shape().MakeRegularPolygon(1.0, 3)
        shape.Transform(transform)
        shape_list.append(shape)'''

        return shape_list

'''
class Level_2(LevelBase):
    def __init__(self):
        super().__init__()

    def MakeWindow(self):
        return Window(complex(-10.0, -10.0), complex(10.0, 10.0))

    def MakeShapes(self):
        shape_list = []

        transform = AffineTransform()
        transform.MakeScale(4.0)
        transform.Concatinate(AffineTransform().MakeTranslation(complex(-2.0, 0.0)))
        shape = Shape().MakeRegularPolygon(1.0, 4)
        shape.Transform(transform)
        shape_list.append(shape)

        transform = AffineTransform()
        transform.MakeScale(4.0)
        transform.Concatinate(AffineTransform().MakeTranslation(complex(2.0, 0.0)))
        shape = Shape().MakeRegularPolygon(1.0, 4)
        shape.Transform(transform)
        shape_list.append(shape)

        return shape_list'''

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--width', help='Specify image width in pixels.  Default is 512.', type=str)
    parser.add_argument('--height', help='Specify image height in pixels.  Default is 512.', type=str)

    args = parser.parse_args()

    image_width = int(args.width) if args.width is not None else 512
    image_height = int(args.height) if args.height is not None else 512

    for level_class in LevelBase.__subclasses__():
        level = level_class()
        level_data = {
            'name': level_class.__name__,
            'image_width': image_width,
            'image_height': image_height,
            'permutation_list': []
        }
        print('Processing %s...' % level_data['name'])
        world_window = level.MakeWindow()
        shape_list = level.MakeShapes()
        for shape in shape_list:
            for i, symmetry in enumerate(shape.symmetry_list):
                print('Processing permutation %d...' % i)
                perm = ImagePermutation(image_width, image_height)
                perm.Generate(world_window, shape, symmetry)
                if not perm.IsValid():
                    raise Exception('Invalid permutation!')
                permutation_data = {
                    'map': perm.map
                    # TODO: We'll also need some hot-spot data here.  Calculate from symmetry transform?
                }
                level_data['permutation_list'].append(permutation_data)
        file = 'levels/' + level_data['name'] + '.json'
        with open(file, 'w') as handle:
            level_data_text = json.dumps(level_data)
            handle.write(level_data_text)

    print('Script complete!')