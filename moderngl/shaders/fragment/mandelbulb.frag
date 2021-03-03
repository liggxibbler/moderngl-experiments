#version 330

#define CAMERA_POS CameraFrag[3].xyz
#define CAMERA_FWD CameraFrag[2].xyz
#define MAX_STEP StepInfo.x
#define MIN_DIST StepInfo.y
#define SMIN_K 1
#define PI 3.14159265

uniform mat4x4 CameraFrag;
uniform vec4 StepInfo;
uniform vec3 LightPos;

uniform vec3 PlanePos;

uniform int Iterations;
uniform int Bailout;
uniform float Power;

in vec3 v_pixray;
out vec4 f_color;

float smin(float a, float b, float k)
{    
    float h = clamp(0.5 + 0.5 * (a - b) / k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

float distance_to_plane(vec3 point, vec3 normal, vec3 p0)
{
    return dot (point - p0, normal) / length(point - p0);
}

float DE(vec3 pos, out int i) {
	vec3 z = pos;
	float dr = 1.0;
	float r = 0.0;
	for (i = 0; i < Iterations ; i++)
    {
		r = length(z);
		if (r>Bailout) break;
		
		// convert to polar coordinates
		float theta = acos(z.z/r);
		float phi = atan(z.y,z.x);
		dr =  pow( r, Power-1.0)*Power*dr + 1.0;
		
		// scale and rotate the point
		float zr = pow( r,Power);
		theta = theta*Power;
		phi = phi*Power;
		
		// convert back to cartesian coordinates
		z = zr*vec3(sin(theta)*cos(phi), sin(phi)*sin(theta), cos(theta));
		z+=pos;
	}
	return 0.5*log(r)*r/dr;
}

float distance(vec3 point, out int iter)
{
    return max(-DE(point, iter), distance_to_plane(point, vec3(0,0,-1), PlanePos));
    //return DE(point, iter);
}

float raymarch(vec3 pos, vec3 ray, out int iter)
{
    float step = 0;
    float dist = MAX_STEP;
    
    while (step < MAX_STEP && dist > MIN_DIST)
    {
        dist = distance(pos + ray * step, iter);
        step = step + dist;
    }

    return step;
}

vec3 GetNormal(vec3 hit, out int iter)
{
    vec2 e = vec2(.001, 0);

    vec3 d1 = vec3(
        distance(hit + e.xyy, iter),
        distance(hit + e.yxy, iter),
        distance(hit + e.yyx, iter)
    );

    vec3 d2 = vec3(
        distance(hit - e.xyy, iter),
        distance(hit - e.yxy, iter),
        distance(hit - e.yyx, iter)
    );

    return normalize(d1 - d2);
}

float shadow(vec3 hit, vec3 hitLightDir, float distToLight, out int iter)
{
    float step = 0;
    float dist = MAX_STEP;
    float res = 1.0f;
    while (step < distToLight && dist > MIN_DIST)
    {
        dist = distance(hit + hitLightDir * step, iter);
        if (dist < MIN_DIST)
            return 0.0;
        step = step + dist;
    }
    return res;
}

void main()
{
    vec3 ray = normalize(v_pixray - CAMERA_POS);

    int iter = 0;
    int iterNorm = 0;
    int iterSh = 0;
    float steps = raymarch(CAMERA_POS, ray, iter);

    if (steps < MAX_STEP)
    {
        vec3 hit = CAMERA_POS + ray * steps;
        vec3 hitToLight = LightPos - hit;
        float attenuation = dot(hitToLight, hitToLight);
        vec3 hitLightDir = normalize(hitToLight);
        vec3 normal = GetNormal(hit, iterNorm);
        //float shadow = softshadow(hit + MIN_DIST * normal, hitLightDir, length(hitToLight), 10);
        float shadow = shadow(hit + 2 * MIN_DIST * normal, hitLightDir, length(hitToLight), iterSh);
        if (shadow == 0)
            shadow = .1;
        
        float diffuse = clamp(dot(hitLightDir, normal), 0, 1);
        vec3 reflect = normalize(2 * dot(hitLightDir, normal) * normal - hitLightDir);
        float specular = clamp(dot(-ray, reflect), 0, 1);
        float shade = step(cos(35*PI/180), dot(CAMERA_FWD, -hitLightDir)) * (diffuse + pow(specular, 32));
        
        float ratio = 5 / dot(hitToLight, hitToLight) * iter / Iterations;

        //f_color = vec4(shade*hitLightDir, 1);        
        //f_color = vec4(vec3(shade * 60), 1);
        //f_color = vec4(vec3(shadow * shade,shadow * shade*.75,shadow * shade*.75)*ratio, 1);
        //f_color = vec4(abs(normal), 1);
        f_color = vec4(vec3(1.0*iter/Iterations),1);
    }
    else
        f_color = vec4(0);
}