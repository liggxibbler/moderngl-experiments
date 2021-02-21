import numpy as np

import moderngl
from example import Example

frag_path = r"shaders\fragment\raymarch.frag"
vert_path = r"shaders\vertex\raymarch.vert"

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
        self.screen_res.value = (.4, .3, 1)

        self.sphere = self.prog['Sphere']
        self.sphere.value = (0, 0, 20, 5)

        self.torus = Torus()
        self.torus.center = self.prog['Torus.center']
        self.torus.center.value = (0, 0, 20)
        self.torus.normal = self.prog['Torus.normal']
        self.torus.normal.value = (0, 0, 1)
        self.torus.radii = self.prog['Torus.radii']
        self.torus.radii.value = (10, 2, 0)

        self.plane = Plane()
        self.plane.point = self.prog['Plane.point']
        self.plane.point.value = (0,-100,0)
        self.plane.normal = self.prog['Plane.normal']
        self.plane.normal.value = (0, 1, 0)

        self.stepinfo = self.prog['StepInfo']
        self.stepinfo.value = (1000, .005, 0, 0)

        self.lightpos = self.prog['LightPos']
        self.lightpos.value = (0, 15, 0)

        self.cam_vert = self.prog['CameraVert']
        self.camera_rt = (1, 0, 0, 0)
        self.camera_up = (0, 1, 0, 0)
        self.camera_fd = (0, 0, 1, 0)
        self.camera_pos = (0, 0, 0, 1)

        self.cam_frag = self.prog["CameraFrag"]
        self.cam_frag.value = (*self.camera_rt, *self.camera_up, *self.camera_fd, *self.camera_pos)

        self.update_camera_value()

        vertices = np.array([-1, 1, -1, -1, 1, -1, 1, 1])

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx._vertex_array(self.prog, [(self.vbo, "2f", "in_vert")])

    def rotate_camera_about_y(self, angle):
        from math import cos, sin, pi        
        self.camera_rt = (cos(angle), 0, sin(angle), 0)
        self.camera_up = (0, 1, 0, 0)
        self.camera_fd = (cos(pi/2 + angle), 0, sin(pi/2 + angle), 0)
        self.update_camera_value()

    def rotate_camera_about_x(self, angle):
        from math import cos, sin, pi
        self.camera_rt = (1, 0, 0, 0)
        self.camera_up = (0, sin(angle + pi /2), cos(angle + pi/2), 0)        
        self.camera_fd = (0, sin(angle), cos(angle), 0)
        self.update_camera_value()

    def rotate_camera_about_z(self, angle):
        from math import cos, sin, pi
        self.camera_rt = (cos(angle), sin(angle), 0, 0)
        self.camera_up = (cos(angle + pi/2), sin(angle + pi /2), 0, 0)
        self.camera_fd = (0, 0, 1, 0)
        self.update_camera_value()

    def update_camera_value(self):        
        self.cam_vert.value = (*self.camera_rt, *self.camera_up, *self.camera_fd, *self.camera_pos)
        self.cam_frag.value = (*self.camera_rt, *self.camera_up, *self.camera_fd, *self.camera_pos)

    def render(self, time, frame_time):
        from math import sin, cos, pi

        self.ctx.clear(0.0, 0.0, 0.0)

        self.torus.center.value = (0, 0, 0)
        self.torus.normal.value = (0, 1, 0)
        self.torus.radii.value = (12, 5, 0)
        
        self.sphere.value = (0, 0, 0, 12)
        #self.plane.value = [(0,0,30), (0, -sin(c), -cos(c))]

        #self.rotate_camera_about_z(sin(time) * pi/2)
        angle = time / 5
        rad = 100 #+ 10 * cos(angle)
        self.camera_pos = (rad * cos(angle), 0, rad * sin(angle), 1)
        self.rotate_camera_about_x(pi/2  + angle)
        self.lightpos.value = (cos(angle) * rad, 0, sin(angle) * rad)
        self.vao.render(moderngl.TRIANGLE_FAN)

        #self.vao.release()
        #self.vbo.release()

if __name__ == '__main__':
    Raymarch.run((1024,768))
