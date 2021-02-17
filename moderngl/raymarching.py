import numpy as np

import moderngl
from example import Example

frag_path = r"shaders\fragment\raymarch.frag"
vert_path = r"shaders\vertex\quad.vert"

with open(frag_path) as frag_file:
    shfragment = frag_file.read()

with open(vert_path) as vert_file:
    shvertex = vert_file.read()

class Torus:
    def __init__(self):
        self.center = None
        self.normal = None
        self.radii = None

class Plane:
    def __init__(self):
        self.point = None
        self.normal = None

class Raymarch(Example):
    title = "Space Fillers"
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader=shvertex,
            fragment_shader=shfragment,
        )

        for x in self.prog:
            print (x)

        self.screen_res = self.prog['ScreenRes']
        self.screen_res.value = (.4, .3)

        self.sphere = self.prog['Sphere']
        self.sphere.value = (0, 0, 20, 5)

        self.torus = Torus()
        self.torus.center = self.prog['Torus.center']
        self.torus.center.value = (0, 0, 20)
        self.torus.normal = self.prog['Torus.normal']
        self.torus.normal.value = (.707, 0, -.707)
        self.torus.radii = self.prog['Torus.radii']
        self.torus.radii.value = (10, 2, 0)

        self.plane = Plane()
        self.plane.point = self.prog['Plane.point']
        self.plane.point.value = (0,-20,0)
        self.plane.normal = self.prog['Plane.normal']
        self.plane.normal.value = (0, 1, 0)

        self.camera = self.prog['CameraDistance']
        self.camera.value = .3

        self.stepinfo = self.prog['StepInfo']
        self.stepinfo.value = (1000, .001, 0, 0)

        self.lightpos = self.prog['LightPos']
        self.lightpos.value = (0, 10, 0)

        vertices = np.array([-1, 1, -1, -1, 1, -1, 1, 1])

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx._vertex_array(self.prog, [(self.vbo, "2f", "in_vert")])

    def render(self, time, frame_time):
        from math import sin, cos, pi

        self.ctx.clear(0.0, 0.0, 0.0)

        rad = 40
        scale = .33
        c = cos(time) * pi/4
        #self.lightpos.value = (cos(time * scale) * rad, 60, 20 + sin(time * scale) * rad)
        self.torus.center.value = (0, 0, 20)
        self.torus.normal.value = (sin(time), 0, cos(time))
        self.torus.radii.value = (12, 5, 0)
        
        self.sphere.value = (0, 10 * cos(time), 20, 5)
        #self.plane.value = [(0,0,30), (0, -sin(c), -cos(c))]

        self.vao.render(moderngl.TRIANGLE_FAN)

        #self.vao.release()
        #self.vbo.release()

if __name__ == '__main__':
    Raymarch.run((1024,768))
