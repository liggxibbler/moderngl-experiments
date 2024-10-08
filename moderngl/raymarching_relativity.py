import numpy as np

import moderngl
from example import Example

res_x = 1920
res_y = 1080

common_path = r"shaders\fragment\common.glsl"
rocket_path = r"shaders\fragment\rocket.glsl"
bufferb_path = r"shaders\fragment\bufferb.glsl"
frag_path = r"shaders\fragment\relativity.frag"
vert_path = r"shaders\vertex\raymarch.vert"
frag_modified_path = r"shaders\fragment\mod.frag"

with open(common_path) as common_file:
    commoncode = "\n" + common_file.read() + "\n"

with open(rocket_path) as rocket_file:
    rocketcode = "\n" + rocket_file.read() + "\n"

with open(bufferb_path) as bufferb_file:
    bufferbcode = "\n" + bufferb_file.read() + "\n"

with open(frag_path) as frag_file:
    shfragment = frag_file.read()
    shfragment = shfragment.replace("###include \"common\"", commoncode)
    shfragment = shfragment.replace("###include \"rocket\"", rocketcode)

with open(frag_modified_path, mode="w") as mod_file:
    mod_file.write(shfragment)

with open(vert_path) as vert_file:
    shvertex = vert_file.read()

def gamma_operator(beta):
        from math import pow
        return pow(1 - beta * beta, -.5)
    
def lorentz(v, c):
    speed = np.linalg.norm(v)
    beta = speed / c
    gamma = gamma_operator(beta)

    v2 = speed * speed
    
    return (1 + (gamma - 1) * v[0] * v[0] / v2, (gamma - 1) * v[0] * v[1] / v2, (gamma - 1) * v[0] * v[2] / v2, -gamma * v[0] / c,
             (gamma - 1) * v[1] * v[1] / v2, 1 + (gamma - 1) * v[1] * v[1] / v2, (gamma - 1) * v[1] * v[2] / v2, -gamma * v[1] / c,
             (gamma - 1) * v[2] * v[0] / v2, (gamma - 1) * v[2] * v[1] / v2, 1 + (gamma - 1) * v[2] * v[2] / v2, -gamma * v[2] / c,
             -gamma * v[0] / c, -gamma * v[1] / c, -gamma * v[2] / c, gamma)

class Raymarch(Example):
    title = "Relativity"
    gl_version = (4, 6)

    def init_keys(self):
        self.keys = {}
        self.keys[self.wnd.keys.W] = False
        self.keys[self.wnd.keys.A] = False
        self.keys[self.wnd.keys.S] = False
        self.keys[self.wnd.keys.D] = False
        self.keys[self.wnd.keys.Q] = False
        self.keys[self.wnd.keys.Z] = False
    
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

        # print out all uniform buffers
        # note: if a uniform is declared but never used, it will be optimized away and the host code won't see it
        for x in self.prog:
            print (x)

        self.transformMatrix = self.prog['transformMatrix']
        self.transformMatrix.value = (1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)

        self.fourvel = self.prog['fourvel']
        self.fourvel.value = (0,0,0,1)

        self.position = self.prog['uposition']
        self.position.value = (0,0,0,0)

        self.boost = self.prog['boost']
        self.boost.value = (0,0,0,0)

        self.orientation = self.prog['orientation']
        self.orientation.value = (1,0,0)


        self.iResolution = self.prog['iResolution']
        self.iResolution.value = (res_x, res_y,0)

        self.iMouse = self.prog['iMouse']
        self.iMouse.value = (0,0,0)

        self.iTimeDelta = self.prog['iTimeDelta']
        self.iTimeDelta.value = 0

        self.screen_res = self.prog['ScreenRes']
        self.screen_res.value = (res_x, res_y, 1)

        vertices = np.array([-1, 1, -1, -1, 1, -1, 1, 1])

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx._vertex_array(self.prog, [(self.vbo, "2f", "in_vert")])
        
    def key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            if key in self.keys:
                self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            if key in self.keys:
                self.keys[key] = False
    
    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        self.iMouse.value = (x, y, 0)

    def handle_input(self):
        boost_increment = .45
        
        if self.keys[self.wnd.keys.A]:
            current_boost = self.boost.value
            current_boost = (current_boost[0], current_boost[1], boost_increment, current_boost[3])
            self.boost.value = tuple(current_boost)

        if self.keys[self.wnd.keys.D]:
            current_boost = self.boost.value
            current_boost = (current_boost[0], current_boost[1], -boost_increment, current_boost[3])
            self.boost.value = tuple(current_boost)

        if self.keys[self.wnd.keys.W]:
            current_boost = self.boost.value
            current_boost = (boost_increment, current_boost[1], current_boost[2], current_boost[3])
            self.boost.value = tuple(current_boost)

        if self.keys[self.wnd.keys.S]:
            current_boost = self.boost.value
            current_boost = (-boost_increment, current_boost[1], current_boost[2], current_boost[3])
            self.boost.value = tuple(current_boost)
        
        if self.keys[self.wnd.keys.Q]:
            current_boost = self.boost.value
            current_boost = (current_boost[0], boost_increment, current_boost[2], current_boost[3])
            self.boost.value = tuple(current_boost)

        if self.keys[self.wnd.keys.Z]:
            current_boost = self.boost.value
            current_boost = (current_boost[0], -boost_increment, current_boost[2], current_boost[3])
            self.boost.value = tuple(current_boost)


    def update_physics(self, dt):
        self.fourvel.value += np.array(self.boost.value) * dt
        self.position.value += np.array(self.fourvel.value) * dt

    def render(self, time, frame_time):
        from math import sin, cos, pi

        self.ctx.clear(0.0, 0.0, 0.0)
        
        self.iTimeDelta.value = frame_time        
        
        self.handle_input()
        self.update_physics(frame_time)

        time2 = time / 2.0        

        rad = 50
        #self.lightpos.value = (0,0,-10)#self.camera_pos[:3]
        #self.lightpos.value = tuple(self.camera_pos[:3])#tuple(-x for x in self.camera_pos[:3])
        self.vao.render(moderngl.TRIANGLE_FAN)

        #self.vao.release()
        #self.vbo.release()

if __name__ == '__main__':
    Raymarch.run((res_x, res_y))