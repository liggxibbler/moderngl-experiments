#version 330

uniform vec3 ScreenRes;
uniform mat4x4 Camera;

in vec2 in_vert;
out vec3 v_pixpos;

void main()
{
    gl_Position = vec4(in_vert.xy, 0.0, 1.0);
    v_pixpos = (Camera * vec4(in_vert, 0, 1)).xyz;
    v_pixpos.xy *= ScreenRes.xy;
    v_pixpos += Camera[2].xyz * ScreenRes.z;
}