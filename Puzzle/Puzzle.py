# Puzzle.py

from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from Math.Polygon import Polygon

class Puzzle(object):
    def __init__(self):
        self.cutter_list = []
        self.shape_list = []
        self.base_image_file = None
        self.x_min = -10.0
        self.x_max = 10.0
        self.y_min = -10.0
        self.y_max = 10.0

    def IsSolved(self):
        pass # The puzzle is solved if all shapes have the identity transform.

    def Manipulate(self):
        # TODO: Here we cut, capture and transform...
        pass

    def GenerateImageFile(self, image_file):
        try:
            texture = GL_INVALID_VALUE

            # Load the raw image RGB data into memory.
            base_image = Image.open(self.base_image_file)
            base_image_rgb = base_image.convert('RGB')
            base_image_data = []
            for i in range(base_image.width):
                for j in range(base_image.height):
                    r, g, b = base_image_rgb.getpixel((i, j))
                    base_image_data += [r, g, b]

            # Create a texture object with the image data.  Note that it is bound.
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, base_image.width, base_image.height, 0, GL_RGB, GL_UNSIGNED_INT, base_image_data)

            # Create a frame-buffer object and bind it for off-screen rendering purposes.
            frame_buffer_list = []
            glGenFramebuffers(1, frame_buffer_list)
            frame_buffer = frame_buffer_list[0]
            glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer)
            print(glCheckFramebufferStatus(GL_FRAMEBUFFER))

            # Setup our initial OpenGL state.
            glClearColor(0.0, 0.0, 0.0, 0.0)
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_TEXTURE_2D)

            # Setup our viewing.
            glViewport(0, 0, base_image.width, base_image.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(self.x_min, self.x_max, self.y_min, self.y_max)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Draw the background.
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex2f(self.x_min, self.y_min)
            glTexCoord2f(1.0, 0.0)
            glVertex2f(self.x_max, self.y_min)
            glTexCoord2f(1.0, 1.0)
            glVertex2f(self.x_max, self.y_max)
            glTexCoord2f(0.0, 1.0)
            glVertex2f(self.x_min, self.y_max)
            glEnd()

            # Draw the foreground shapes.
            for shape in self.shape_list:
                shape.Render(self)

            # All rendering done, now read the frame-buffer into memory as an image, and save to disk.
            stride = 0 # Zero bytes between scan-lines.
            orientation = 1 # First scan-line is top (not bottom, -1).
            result_image_data = glReadPixels(0, 0, base_image.width, base_image.height, GL_RGB, GL_FLOAT)
            result_image = Image.open(image_file, 'w')
            result_image.frombuffer('RGB', base_image.width * base_image.height, result_image_data, 'raw', stride, orientation)
            result_image.save()

        except Exception as ex:
            raise ex

        finally:
            if texture != GL_INVALID_VALUE:
                glDeleteTextures(texture)
            if len(frame_buffer_list) > 0:
                glDeleteFramebuffers(1, frame_buffer_list)

class Shape(object):
    def __init__(self):
        self.local_polygon = None
        # This might suffer from accumulated round-off error.  Hmmm...
        # To combat that, would keeping a history of transforms help, even if it slowed things down?
        self.local_to_world_transform = None

    def GenerateWorldPolygon(self):
        world_polygon = Polygon()
        for point in self.local_polygon.point_list:
            point = self.local_to_world_transform.Transform(point)
            world_polygon.point_list.append(point)
        return world_polygon

    def Render(self, puzzle):
        world_polygon = self.GenerateWorldPolygon()
        world_polygon.Tessellate()
        world_to_local_transform = self.local_to_world_transform.Inverted()
        glBegin(GL_TRIANGLES)
        try:
            for triangle in world_polygon.triangle_list:
                for i in range(3):
                    world_point = triangle.vertex_list[i]
                    local_point = world_to_local_transform.Transform(world_point)
                    u = (local_point.x - puzzle.x_min) / (puzzle.x_max - puzzle.x_min)
                    v = (local_point.y - puzzle.y_min) / (puzzle.y_max - puzzle.y_min)
                    glTexCoord2f(u, v)
                    glVertex2f(world_point.x, world_point.y)
        finally:
            glEnd()

class Cutter(object):
    def __init__(self):
        self.polygon = None