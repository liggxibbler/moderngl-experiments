#version 330

uniform vec3 ScreenRes;
uniform mat4x4 CameraVert;

in vec2 in_vert;
out vec3 v_pixpos;

void main()
{
    gl_Position = vec4(in_vert, 0.0, 1.0);    
    v_pixpos = vec3(in_vert * ScreenRes.xy, 0);
    v_pixpos = (CameraVert * vec4(v_pixpos, 1)).xyz;    
    v_pixpos += CameraVert[2].xyz * ScreenRes.z;
}