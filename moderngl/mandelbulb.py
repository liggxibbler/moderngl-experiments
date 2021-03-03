import numpy as np

import moderngl
from example import Example

frag_path = r"shaders\fragment\mandelbulb.frag"
vert_path = r"shaders\vertex\raymarch.vert"

with open(frag_path) as frag_file:
    shfragment = frag_file.read()

with open(vert_path) as vert_file:
    shvertex = vert_file.read()

class Raymarch(Example):
    title = "Space Fillers"
    gl_version = (3, 3)

    def init_keys(self):
        self.keys = {}
        self.keys[self.wnd.keys.W] = False
        self.keys[self.wnd.keys.A] = False
        self.keys[self.wnd.keys.S] = False
        self.keys[self.wnd.keys.D] = False
        self.keys[self.wnd.keys.Q] = False
        self.keys[self.wnd.keys.E] = False
        self.keys[self.wnd.keys.Z] = False
        self.keys[self.wnd.keys.C] = False
    
    def get_key(self, key):
        if key in self.keys:
            return self.keys[key]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_keys()

        self.prog = self.ctx.program(
            vertex_shader=shvertex,
            fragment_shader=shfragment,
        )

        for x in self.prog:
            print (x)

        self.screen_res = self.prog['ScreenRes']
        self.screen_res.value = (.4, .3, 1)

        self.stepinfo = self.prog['StepInfo']
        self.stepinfo.value = (1000, .005, 0, 0)

        self.lightpos = self.prog['LightPos']
        self.lightpos.value = (0, 5, -10)

        self.planepos = self.prog["PlanePos"]
        self.planepos.value = (0,0,0)

        self.camera_rt = (1, 0, 0, 0)
        self.camera_up = (0, 1, 0, 0)
        self.camera_fd = (0, 0, 1, 0)
        self.camera_pos = (0, 0, -5, 1)

        self.cam_vert = self.prog['CameraVert']
        self.cam_frag = self.prog["CameraFrag"]
        self.update_camera_value()        

        self.iterations = self.prog['Iterations']
        self.bailout = self.prog['Bailout']
        self.power = self.prog['Power']

        self.iterations.value = 10
        self.bailout.value = 4
        self.power.value = 8


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

    def key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            if key in self.keys:
                self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            if key in self.keys:
                self.keys[key] = False
    
    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        from math import sin, cos
        if (self.wnd._mouse_buttons.left):
            s = sin(-dx * .005)
            c = cos(-dx * .005)            
            print (self.camera_fd)
            self.camera_fd = (
                self.camera_fd[0] * c - self.camera_fd[2] * s,
                0,
                self.camera_fd[0] * s + self.camera_fd[2] * c,
                0
            )
            self.camera_rt = (self.camera_fd[2], 0, -self.camera_fd[0], 0)
            
            print (self.camera_fd)
            self.update_camera_value()

    def handle_input(self):
        dx = .1
        
        if self.keys[self.wnd.keys.W]:
            pos = np.array(self.camera_pos) + dx * np.array(self.camera_fd)
            pos[3] = 1
            self.camera_pos = tuple(pos)
            self.update_camera_value()
        if self.keys[self.wnd.keys.S]:
            pos = np.array(self.camera_pos) - dx * np.array(self.camera_fd)
            pos[3] = 1
            self.camera_pos = tuple(pos)
            self.update_camera_value()
        if self.keys[self.wnd.keys.A]:
            pos = np.array(self.camera_pos) - dx * np.array(self.camera_rt)
            pos[3] = 1
            self.camera_pos = tuple(pos)
            self.update_camera_value()
        if self.keys[self.wnd.keys.D]:
            pos = np.array(self.camera_pos) + dx * np.array(self.camera_rt)
            pos[3] = 1
            self.camera_pos = tuple(pos)
            self.update_camera_value()
        if self.keys[self.wnd.keys.Q]:
            pos = np.array(self.camera_pos) + dx * np.array(self.camera_up)
            pos[3] = 1
            self.camera_pos = tuple(pos)
            self.update_camera_value()
        if self.keys[self.wnd.keys.E]:
            pos = np.array(self.camera_pos) - dx * np.array(self.camera_up)
            pos[3] = 1
            self.camera_pos = tuple(pos)
            self.update_camera_value()
        if self.keys[self.wnd.keys.Z]:
            temp = np.array(self.planepos.value) + dx * np.array(self.camera_fd[:3])
            self.planepos.value = tuple(temp)
        if self.keys[self.wnd.keys.C]:
            temp = np.array(self.planepos.value) - dx * np.array(self.camera_fd[:3])
            self.planepos.value = tuple(temp)

    def render(self, time, frame_time):
        from math import sin, cos, pi

        self.ctx.clear(0.0, 0.0, 0.0)

        self.handle_input()

        time2 = time / 6.0
        self.power.value = (time2 % 256)

        rad = 50
        #self.lightpos.value = (0,0,-10)#self.camera_pos[:3]
        self.lightpos.value = self.camera_pos[:3]
        self.vao.render(moderngl.TRIANGLE_FAN)

        #self.vao.release()
        #self.vbo.release()

if __name__ == '__main__':
    Raymarch.run((1024,768))
