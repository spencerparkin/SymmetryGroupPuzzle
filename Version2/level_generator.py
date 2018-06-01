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

def SquareDistance(point_a, point_b):
    return (point_a.real - point_b.real)**2 + (point_a.imag - point_b.imag)**2

class Shape(object):
    def __init__(self):
        self.point_list = []
        self.triangle_list = [] # These must be wound CCW in the plane.
        # There might be a way to calculate the symmetries of the shape
        # as a function of the shape itself, but until I can figure that
        # out, the symmetries will be computed using human-knowledge of the shape.
        # Not all symmetries of the shape need appear in this list.  We only need
        # enough of them to generate the group of symmetries of the shape.  We
        # actually want a bit more than that.  We want as many as are convenient
        # for the user who is working in the group.
        self.symmetry_list = []

    def ContainsPoint(self, point, epsilon=1e-9):
        for triangle in self.triangle_list:
            for i in range(3):
                j = (i + 1) % 3
                vector_a = self.point_list[triangle[i]] - point
                vector_b = self.point_list[triangle[j]] - point
                det = Cross(vector_a, vector_b)
                if det <= -epsilon:
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
        if not inverse.Invert():
            raise Exception('Failed to invert symmetry transform.')
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
        self.symmetry_list.append(AffineTransform().MakeRotation(-2.0 * math.pi / float(sides)))
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
            self.translation = self.Transform(-self.translation, False)
            return True
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
        self.map = None
        self.width = width
        self.height = height

    def Generate(self, world_window, shape, symmetry):
        
        print('Building trial map...')
        trial_map = [[[] for i in range(self.height)] for j in range(self.width)]
        image_window = Window(complex(0.0, 0.0), complex(float(self.width - 1), float(self.height - 1)))
        for i in range(self.width):
            for j in range(self.height):
                source_image_point = complex(float(i), float(j))
                source_world_point = world_window.Map(source_image_point, image_window)
                if shape.ContainsPoint(source_world_point):
                    target_world_point = symmetry.Transform(source_world_point)
                    if not shape.ContainsPoint(target_world_point):
                        raise Exception('Invalid symmetry detected!')
                    target_image_point = image_window.Map(target_world_point, world_window)
                else:
                    target_image_point = source_image_point
                jump = {
                    'source_image_point': source_image_point,
                    'target_image_point': target_image_point
                }
                coords = (int(round(target_image_point.real)), int(round(target_image_point.imag)))
                jump_list = trial_map[coords[0]][coords[1]]
                jump_list.append(jump)

        print('Analyzing trial map...')
        empty_slots_list = []
        overcrowded_slots_list = []
        for i in range(self.width):
            for j in range(self.height):
                jump_list = trial_map[i][j]
                if len(jump_list) == 0:
                    empty_slots_list.append((i, j))
                elif len(jump_list) > 1:
                    overcrowded_slots_list.append((i, j))
        print('Found %d empty slots.' % len(empty_slots_list))
        print('Found %d over-crowded slots.' % len(overcrowded_slots_list))
        
        # I'm not sure that this is the best way to resolve the map.
        # What this boils down to is how to map N points to N other points where the point pairs
        # of the mapping form line-segments of the smallest possible total length.
        print('Resolving trial map...')
        for overcrowded_slot in overcrowded_slots_list:
            image_point = complex(float(overcrowded_slot[0]), float(overcrowded_slot[1]))
            jump_list = trial_map[overcrowded_slot[0]][overcrowded_slot[1]]
            while len(jump_list) > 1:
                largest_square_distance = 0.0
                j = -1
                for i, jump in enumerate(jump_list):
                    square_distance = SquareDistance(jump['target_image_point'], image_point)
                    if square_distance > largest_square_distance:
                        j = i
                relocate_jump = jump_list[j]
                del jump_list[j]
                smallest_square_distance = None
                j = -1
                for i, empty_slot in enumerate(empty_slots_list):
                    image_point = complex(float(empty_slot[0]), float(empty_slot[1]))
                    square_distance = SquareDistance(jump['target_image_point'], image_point)
                    if smallest_square_distance is None or square_distance < smallest_square_distance:
                        smallest_square_distance = square_distance
                        j = i
                empty_slot = empty_slots_list[j]
                trial_map[empty_slot[0]][empty_slot[1]].append(relocate_jump)
                del empty_slots_list[j]
                
        print('Building final map...')
        self.map = [[None for i in range(self.height)] for j in range(self.width)]
        for i in range(self.width):
            for j in range(self.height):
                jump = trial_map[i][j][0]
                coords = (int(jump['source_image_point'].real), int(jump['source_image_point'].imag))
                self.map[coords[0]][coords[1]] = (i, j)

    def IsValid(self):
        # This is just a sanity check.
        count_matrix = [[0 for j in range(self.width)] for i in range(self.height)]
        for i in range(self.width):
            for j in range(self.height):
                coords = self.map[i][j]
                count_matrix[coords[0]][coords[1]] += 1
        for i in range(self.width):
            for j in range(self.height):
                if count_matrix[i][j] != 1:
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

        transform = AffineTransform()
        transform.MakeScale(4.0)
        transform.Concatinate(AffineTransform().MakeTranslation(complex(-2.5, 0.0)))
        shape = Shape().MakeRegularPolygon(1.0, 3)
        shape.Transform(transform)
        shape_list.append(shape)

        transform = AffineTransform()
        transform.MakeScale(4.0)
        transform.Concatinate(AffineTransform().MakeRotation(math.pi / 3.0))
        transform.Concatinate(AffineTransform().MakeTranslation(complex(2.5, 0.0)))
        shape = Shape().MakeRegularPolygon(1.0, 3)
        shape.Transform(transform)
        shape_list.append(shape)

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
        for i, shape in enumerate(shape_list):
            print('Processing shape %d...' % i)
            for j, symmetry in enumerate(shape.symmetry_list):
                print('Processing permutation %d...' % j)
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