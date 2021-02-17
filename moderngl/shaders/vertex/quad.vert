#version 330

uniform vec2 ScreenRes;

in vec2 in_vert;
out vec2 v_pixpos;

void main() {
    gl_Position = vec4(in_vert.xy, 0.0, 1.0);
    v_pixpos = in_vert * ScreenRes;
}