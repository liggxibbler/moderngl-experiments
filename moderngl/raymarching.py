import numpy as np

import moderngl
from example import Example

class Raymarch(Example):
    title = "Space Fillers"
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform vec2 ScreenRes;

                in vec2 in_vert;
                out vec2 v_pixpos;

                void main() {
                    gl_Position = vec4(in_vert.xy, 0.0, 1.0);
                    v_pixpos = in_vert * ScreenRes;
                }
            ''',
            fragment_shader='''
                #version 330

                #define MAX_STEP StepInfo.x
                #define MIN_DIST StepInfo.y

                uniform float CameraDistance;
                uniform vec4 Sphere;
                uniform vec4 StepInfo;
                uniform vec3 LightPos;

                in vec2 v_pixpos;
                out vec4 f_color;

                float distance_to_sphere(vec3 point)
                {
                    return length(point - Sphere.xyz) - Sphere.w;
                }

                float distance_to_plane(vec3 point)
                {
                    return point.y + 20;
                }

                float distance(vec3 pos)
                {
                    return min(distance_to_sphere(pos), distance_to_plane(pos));
                    //return distance_to_sphere(pos);
                }

                void main() {
                    float step = 0;
                    float dist = 100000;
                    vec3 ray = normalize(vec3(v_pixpos, CameraDistance));

                    while (step < MAX_STEP && dist > MIN_DIST)
                    {
                        dist = distance(ray * step);
                        step = step + dist;
                    }

                    if (step >= MAX_STEP)
                        f_color = vec4(0, 0, 0, 1);
                    else
                    {
                        vec3 hit = ray * step;
                        
                        //vec3 normal = (hit - Sphere.xyz) / Sphere.w;
                        float dx = distance(hit + vec3(MIN_DIST, 0, 0));
                        float dy = distance(hit + vec3(0, MIN_DIST, 0));
                        float dz = distance(hit + vec3(0, 0, MIN_DIST));
                        vec3 normal = normalize((vec3(dx, dy, dz) - distance(hit)) / MIN_DIST);
                        
                        vec3 hitToLight = normalize(LightPos - hit);
                        float diffuse = clamp(dot(hitToLight, normal), 0, 1);
                        vec3 reflect = normalize(2 * dot(hitToLight, normal) * normal - hitToLight);
                        float specular = clamp(dot(-ray, reflect), 0, 1);
                        float shade = diffuse + pow(specular, 64);
                        //f_color = vec4(normal, LightPos.x);
                        f_color = vec4(vec3(shade), 1);
                    }
                }
            ''',
        )

        #self.timme = self.prog['Time']
        self.screen_res = self.prog['ScreenRes']
        self.screen_res.value = (10, 10)

        self.sphere = self.prog['Sphere']
        self.sphere.value = (0, 0, 30, 20)

        self.camera = self.prog['CameraDistance']
        self.camera.value = 5

        self.stepinfo = self.prog['StepInfo']
        self.stepinfo.value = (1000, .0001, 0, 0)

        self.lightpos = self.prog['LightPos']
        self.lightpos.value = (0, 0, 0)

        #self.texture = self.load_texture_2d('buildings.jpg')
        #self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        vertices = np.array([-1, 1, -1, -1, 1, -1, 1, 1])

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        #self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')
        self.vao = self.ctx._vertex_array(self.prog, [(self.vbo, "2f", "in_vert")])

    def render(self, time, frame_time):
        from math import sin, cos

        self.ctx.clear(0.0, 0.0, 0.0)

        rad = 40
        self.lightpos.value = (40 * cos(time), 40 * sin(time), -10)

        self.vao.render(moderngl.TRIANGLE_FAN)

        #self.vao.release()
        #self.vbo.release()

if __name__ == '__main__':
    Raymarch.run((512,512))
