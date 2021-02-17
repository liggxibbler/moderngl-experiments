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
                uniform vec3[2] Plane;
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
                    //return 40 - point.z;
                    return dot (point - Plane[0], Plane[1]);
                }

                float distance(vec3 pos)
                {
                    //return distance_to_plane(pos) - distance_to_sphere(pos);
                    return min(distance_to_sphere(pos), distance_to_plane(pos));
                    //return distance_to_plane(pos);
                }

                float raymarch(vec3 pos, vec3 ray)
                {
                    float step = 0;
                    float dist = 100000;
                    
                    while (step < MAX_STEP && dist > MIN_DIST)
                    {
                        dist = distance(pos + ray * step);
                        step = step + dist;
                    }

                    return step;
                }

                void main() {
                    vec3 pos = vec3(v_pixpos, CameraDistance);
                    vec3 ray = normalize(pos);

                    float step = raymarch(vec3(0), ray);

                    if (step < MAX_STEP)
                    {
                        vec3 hit = ray * step;

                        float dx = distance(hit + vec3(MIN_DIST, 0, 0));
                        float dy = distance(hit + vec3(0, MIN_DIST, 0));
                        float dz = distance(hit + vec3(0, 0, MIN_DIST));
                        vec3 normal = normalize((vec3(dx, dy, dz) - distance(hit)) / MIN_DIST);

                        vec3 hitToLight = LightPos - hit;
                        vec3 hitLightDir = normalize(hitToLight);
                        vec3 offset = hit + normal * 2 * MIN_DIST;
                        vec3 offsetDir = normalize(LightPos - offset);
                        float distLight = raymarch(offset, offsetDir);
                        
                        float diffuse = clamp(dot(hitLightDir, normal), 0, 1);
                        vec3 reflect = normalize(2 * dot(hitLightDir, normal) * normal - hitLightDir);
                        float specular = clamp(dot(-ray, reflect), 0, 1);
                        float shade = diffuse + pow(specular, 64);
                        
                        //f_color = vec4(shade*hitLightDir, 1);
                        
                        if (distLight <= length(hitToLight))
                        {                            
                            shade *= .0;
                        }
                        f_color = vec4(vec3(shade), 1);
                        //f_color = vec4(normal, 1);
                    }
                    else
                        f_color = vec4(0,0,0,1);
                }
            ''',
        )

        self.screen_res = self.prog['ScreenRes']
        self.screen_res.value = (.4, .3)

        self.sphere = self.prog['Sphere']
        self.sphere.value = (0, 0, 50, 40)

        self.plane = self.prog['Plane']
        self.plane.value = [(0,0,50), (-.57, .57, -.57)]

        self.camera = self.prog['CameraDistance']
        self.camera.value = .1

        self.stepinfo = self.prog['StepInfo']
        self.stepinfo.value = (1000, .001, 0, 0)

        self.lightpos = self.prog['LightPos']
        self.lightpos.value = (0, 0, 0)

        vertices = np.array([-1, 1, -1, -1, 1, -1, 1, 1])

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx._vertex_array(self.prog, [(self.vbo, "2f", "in_vert")])

    def render(self, time, frame_time):
        from math import sin, cos, pi

        self.ctx.clear(0.0, 0.0, 0.0)

        rad = 70
        scale = 1
        c = cos(time * scale) * rad
        s = sin(time * scale) * rad
        self.lightpos.value = (0, 0, 0)
        self.plane.value = [(0,0,30), (cos(pi/4), sin(pi/4) * sin(time), sin(pi/4) * cos(time))]

        self.vao.render(moderngl.TRIANGLE_FAN)

        #self.vao.release()
        #self.vbo.release()

if __name__ == '__main__':
    Raymarch.run((1024,768))
