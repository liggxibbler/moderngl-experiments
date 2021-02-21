#version 330

#define MAX_STEP StepInfo.x
#define MIN_DIST StepInfo.y
#define SMIN_K 1

struct TorusStruct
{
    vec3 center;
    vec3 normal;
    vec3 radii;
};

struct PlaneStruct
{
    vec3 point;
    vec3 normal;
};

uniform mat4x4 CameraFrag;
uniform PlaneStruct Plane;
uniform TorusStruct Torus;
uniform vec4 Sphere;
uniform vec4 StepInfo;
uniform vec3 LightPos;

in vec3 v_pixpos;
out vec4 f_color;

float smin(float a, float b, float k)
{    
    float h = clamp(0.5 + 0.5 * (a - b) / k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}


float distance_to_torus(vec3 p)
{
    vec3 g = dot(p - Torus.center, Torus.normal) * Torus.normal;
    vec3 pp = p - g;
    vec3 m = Torus.center + normalize(pp - Torus.center) * Torus.radii.x;
    return length((p - m)) - Torus.radii.y;
}

float distance_to_sphere(vec3 point)
{
    return length(point - Sphere.xyz) - Sphere.w;
}

float distance_to_plane(vec3 point)
{
    //return 40 - point.z;
    return dot (point - Plane.point, Plane.normal);
}

float distance_to_box(vec3 point)
{
    vec3 center = vec3(0);
    float side = 10.0f;
    vec3 q = abs(point - center) - side;
    float dist =  length(max(q, 0));
    return dist + min(max(q.x,max(q.y,q.z)),0.0);
}

float distance(vec3 point)
{
    float factor = 30;
    vec3 pos = mod(point, factor * 2) - factor;
    float dist = smin(distance_to_sphere(pos), distance_to_plane(pos), SMIN_K);
    dist = smin(dist, distance_to_torus(pos), SMIN_K);
    //dist = max(-dist, distance_to_torus(pos));
    return max(distance_to_box(pos), -distance_to_sphere(pos)) + (dist-dist);
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
    vec3 pos = v_pixpos;
    vec3 ray = normalize(pos - CameraFrag[3].xyz);

    float step = raymarch(CameraFrag[3].xyz, ray);

    if (step < MAX_STEP)
    {
        vec3 hit = CameraFrag[3].xyz + ray * step;

        float e = .01;

        vec3 d1 = vec3(
            distance(hit + vec3(e,0,0)),
            distance(hit + vec3(0,e,0)),
            distance(hit + vec3(0,0,e))
        );

        vec3 d2 = vec3(
            distance(hit - vec3(e,0,0)),
            distance(hit - vec3(0,e,0)),
            distance(hit - vec3(0,0,e))
        );

        vec3 normal = normalize(d1 - d2);

        vec3 hitToLight = LightPos - hit;
        vec3 hitLightDir = normalize(hitToLight);
        vec3 offset = hit + normal * 2 * MIN_DIST;
        vec3 offsetDir = normalize(LightPos - offset);
        float distLight = raymarch(offset, offsetDir);
        
        float diffuse = clamp(dot(hitLightDir, normal), 0, 1);
        vec3 reflect = normalize(2 * dot(hitLightDir, normal) * normal - hitLightDir);
        float specular = clamp(dot(-ray, reflect), 0, 1);
        float shade = (diffuse + pow(specular, 64)) / sqrt(dot(hitToLight, hitToLight));
        
        //f_color = vec4(shade*hitLightDir, 1);
        
        if (distLight <= length(hitToLight))
        {            
            shade = 0;
        }
        //f_color = vec4(vec3(shade * 60), 1);
        f_color = vec4(abs(normal) * shade * 70, 1);
    }
    else
        f_color = vec4(0,Plane.normal.x,Plane.point.x,Sphere.x);
}