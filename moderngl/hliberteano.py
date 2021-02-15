import numpy as np

import moderngl
from example import Example

def HilbertCurve(n):
    points = []
    ps = np.array([
        [-.5, -.5],
        [-.5, .5], 
        [.5, .5], 
        [.5, -.5]
    ])
    Hilbert(ps, n, points)
    return points

def Hilbert(ps, n, points):
    if n == 0:
        points.extend([ps[0][0], ps[0][1], len(points)])
        points.extend([ps[1][0], ps[1][1], len(points)])
        points.extend([ps[2][0], ps[2][1], len(points)])
        points.extend([ps[3][0], ps[3][1], len(points)])
    else:
        c = (ps[2] + ps[0]) * .5

        p0 = (ps[0] - c) * .5
        p1 = (ps[1] - c) * .5
        p2 = (ps[2] - c) * .5
        p3 = (ps[3] - c) * .5

        Hilbert([ps[0] + p0, ps[0] + p3, ps[0] + p2, ps[0] + p1], n - 1, points)
        Hilbert([ps[1] + p0, ps[1] + p1, ps[1] + p2, ps[1] + p3], n - 1, points)
        Hilbert([ps[2] + p0, ps[2] + p1, ps[2] + p2, ps[2] + p3], n - 1, points)
        Hilbert([ps[3] + p2, ps[3] + p1, ps[3] + p0, ps[3] + p3], n - 1, points)

def PeanoCurve(n):
    points = []
    ps = [
        [-1, 1],
        [1, 1],
        [1, 0],
        [-1, 0],
        [-1, -1],
        [1, -1]
    ]
    ps = np.array(ps) * 2 / 3
    Peano(ps, n, points)
    return points

def Peano(ps, n, points):
    if n == 0:
        points.extend([ps[0][0], ps[0][1], len(points)])
        points.extend([ps[1][0], ps[1][1], len(points)])
        points.extend([ps[2][0], ps[2][1], len(points)])
        points.extend([ps[3][0], ps[3][1], len(points)])
        points.extend([ps[4][0], ps[4][1], len(points)])
        points.extend([ps[5][0], ps[5][1], len(points)])
    else:
        c = []
        c.append(ps[0])
        c.append((ps[0] + ps[1]) * .5)
        c.append(ps[1])
        c.append(ps[2])
        c.append((ps[3] + ps[2]) * .5)
        c.append(ps[3])
        c.append(ps[4])
        c.append((ps[4] + ps[5]) * .5)
        c.append(ps[5])
        
        w = (c[5] - c[4]) / 3
        e = (c[3] - c[4]) / 3
        nn = (c[1] - c[4]) / 3
        ss = (c[7] - c[4]) / 3

        nw = (c[0] - c[4]) / 3
        ne = (c[2] - c[4]) / 3
        se = (c[8] - c[4]) / 3
        sw = (c[6] - c[4]) / 3

        Peano([c[0] + nw, c[0] + ne, c[0] + e, c[0] + w, c[0] + sw, c[0] + se], n-1, points)
        #Peano([c[1] + sw, c[1] + se, c[1] + e, c[1] + w, c[1] + nw, c[1] + ne], n-1, points)
        Peano([c[1] + sw, c[1] + nw, c[1] + nn, c[1] + ss, c[1] + se, c[1] + ne], n-1, points)
        Peano([c[2] + nw, c[2] + ne, c[2] + e, c[2] + w, c[2] + sw, c[2] + se], n-1, points)
        #Peano([c[3] + ne, c[3] + nw, c[3] + w, c[3] + e, c[3] + se, c[3] + sw], n-1, points)
        Peano([c[3] + ne, c[3] + se, c[3] + ss, c[3] + nn, c[3] + nw, c[3] + sw], n-1, points)
        Peano([c[4] + se, c[4] + sw, c[4] + w, c[4] + e, c[4] + ne, c[4] + nw], n-1, points)
        #Peano([c[5] + ne, c[5] + nw, c[5] + w, c[5] + e, c[5] + se, c[5] + sw], n-1, points)
        Peano([c[5] + ne, c[5] + se, c[5] + ss, c[5] + nn, c[5] + nw, c[5] + sw], n-1, points)
        Peano([c[6] + nw, c[6] + ne, c[6] + e, c[6] + w, c[6] + sw, c[6] + se], n-1, points)
        #Peano([c[7] + sw, c[7] + se, c[7] + e, c[7] + w, c[7] + nw, c[7] + ne], n-1, points)
        Peano([c[7] + sw, c[7] + nw, c[7] + nn, c[7] + ss, c[7] + se, c[7] + ne], n-1, points)
        Peano([c[8] + nw, c[8] + ne, c[8] + e, c[8] + w, c[8] + sw, c[8] + se], n-1, points)

def line_map_segment(segment, z):
    return z * (segment[1] - segment[0]) + segment[0]

def line_map_circle(hole_ratio, rounds, z):
    arc = z * 2 * np.math.pi * rounds
    return np.array([np.math.cos(arc), np.math.sin(arc)]) * (z * (1 - hole_ratio) + hole_ratio)

def line_map_lissajous(px, py, z):
    arc = z * 2 * np.math.pi
    return np.array([np.math.cos(arc * px), np.math.sin(arc * py)])

points = HilbertCurve(8)
#points = PeanoCurve(5)

print(f"there are {len(points)} points")

segment = np.array([[-1, 1],[1, -1]])
#segment = np.array([[-1, -.5], [.75, .25]])

line_diff = []

for idx in range(0, len(points), 3):
    z = points[idx + 2] / len(points)
    coords = line_map_lissajous(221, 222, z)
    #coords = line_map_circle(.1, 1000, z)
    #coords = line_map_segment(segment, z)
    coords = np.array([points[idx], points[idx + 1]]) - coords
    line_diff.extend([coords[0], coords[1], 0])

points = np.ndarray.flatten(np.array(points))
line_diff = np.ndarray.flatten(np.array(line_diff))

period = 10

class Fractal(Example):
    title = "Space Fillers"
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec3 in_vert;
                out vec3 v_text;

                void main() {                    
                    gl_Position = vec4(in_vert.xy, 0.0, 1.0);
                    v_text.xy = (in_vert.xy + 1) / 2;
                    v_text.z = in_vert.z;
                }
            ''',
            fragment_shader='''
                #version 330

                #define PI 3.14159265
                #define TAU 6.283185307179586
                #define POW 2

                in vec3 v_text;
                out vec4 f_color;

                //uniform sampler2D Texture;                
                uniform int Time;
                uniform float Count;

                void main() {                    
                    float x = Time / Count;
                    
                    //vec4 c = texture(Texture, v_text.xy);
                    
                    float d = v_text.z / Count;

                    float r = pow((sin((d - 2 * x) * TAU) + 1 ) * .5, POW / 2);                    
                    float g = pow((sin((d + 7 * x) * TAU) + 1 ) * .5, POW);                    
                    float b = pow((cos((d - 19 * x) * TAU) + 1 ) * .5, POW / 3);                    

                    //f_color = vec4(.2 + .3 * d, d, 1 - d, Time);
                    f_color = vec4(r, g, b, x);
                }
            ''',
        )

        self.timme = self.prog['Time']
        self.countt = self.prog['Count']

        self.countt.value = len(points)

        #self.texture = self.load_texture_2d('grass.jpg')
        #self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        vertices = np.array(points)

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)

        #self.seed.value = (time, time)
        t = int(time * len(points) / period) % (len(points) * 2 + 1)
        if (t <= len(points)):
            k = 1 - t / len(points)
        else:
            k = (t - len(points)) / len(points)
        self.timme.value = t
        vertices = points - line_diff * k

        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

        #self.texture.use()
        self.vao.render(moderngl.LINE_STRIP)

        self.vao.release()
        self.vbo.release()

if __name__ == '__main__':
    Fractal.run()
