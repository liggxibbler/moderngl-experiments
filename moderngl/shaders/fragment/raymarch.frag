#version 330

#define MAX_STEP StepInfo.x
#define MIN_DIST StepInfo.y
#define SMIN_K 1

uniform float CameraDistance;
uniform vec3[2] Plane;
uniform vec3[3] Torus;
uniform vec4 Sphere;
uniform vec4 StepInfo;
uniform vec3 LightPos;

in vec2 v_pixpos;
out vec4 f_color;

float smin(float a, float b, float k)
{    
    float h = clamp(0.5 + 0.5*(a-b)/k, 0.0, 1.0);
    return mix(a, b, h) - k*h*(1.0-h);
}

float distance_to_torus(vec3 p)
{
    vec3 g = dot(p - Torus[0], Torus[1]) * Torus[1];
    vec3 pp = p - g;
    vec3 m = Torus[0] + normalize(pp - Torus[0]) * Torus[2].x;
    return length((p - m)) - Torus[2].y;
}

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
    float dist = smin(distance_to_sphere(pos), distance_to_plane(pos), SMIN_K);
    //dist = smin(dist, distance_to_torus(pos), SMIN_K);
    dist = max(-dist, distance_to_torus(pos));
    return dist;
}

float raymarch(vec3 pos, vec3 ray)
{
    float step = 0;
    float dist = MAX_STEP;
    
    while (step < MAX_STEP && dist > MIN_DIST)
    {
        dist = distance(pos + ray * step);
        step = step + dist;
    }

    return step;
}

void main()
{
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
            shade = 0;
        }
        f_color = vec4(vec3(shade), 1);
        //f_color = vec4(normal, 1);
    }
    else
        f_color = vec4(0,Plane[1].x,Plane[0].x,Sphere.x);
}