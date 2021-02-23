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

vec3 GetNormal(vec3 hit)
{
    vec2 e = vec2(.01, 0);

    vec3 d1 = vec3(
        distance(hit + e.xyy),
        distance(hit + e.yxy),
        distance(hit + e.yyx)
    );

    vec3 d2 = vec3(
        distance(hit - e.xyy),
        distance(hit - e.yxy),
        distance(hit - e.yyx)
    );

    return normalize(d1 - d2);
}
float softshadow(vec3 hit, vec3 hitLightDir, float distToLight, float k)
{
    float step = 0;
    float dist = MAX_STEP;
    
    float ph = 1e20;

    float res = 1.0;

    while (step < distToLight && dist > MIN_DIST)
    {
        dist = distance(hit + hitLightDir * step);
        if (dist < MIN_DIST)
            return 0.0;
        float y = dist * dist / (2.0 * ph);
        float d = sqrt(dist*dist - y*y);
        res = min(res, k * d / max(0.0, step -y));
        ph = dist;
        step = step + dist;
    }

    return res;
}

void main()
{
    vec3 pos = v_pixpos;
    vec3 ray = normalize(pos - CameraFrag[3].xyz);

    float step = raymarch(CameraFrag[3].xyz, ray);

    if (step < MAX_STEP)
    {
        vec3 hit = CameraFrag[3].xyz + ray * step;
        vec3 hitToLight = LightPos - hit;
        vec3 hitLightDir = normalize(hitToLight);
        vec3 normal = GetNormal(hit);
        float shadow = softshadow(hit + MIN_DIST * normal, hitLightDir, length(hitToLight), 5);
        
        float diffuse = clamp(dot(hitLightDir, normal), 0, 1);
        vec3 reflect = normalize(2 * dot(hitLightDir, normal) * normal - hitLightDir);
        float specular = clamp(dot(-ray, reflect), 0, 1);
        float shade = diffuse + pow(specular, 64);
        
        //f_color = vec4(shade*hitLightDir, 1);        
        //f_color = vec4(vec3(shade * 60), 1);
        f_color = vec4(vec3(shadow * shade), 1);
        //f_color = vec4(abs(normal), 1);
    }
    else
        f_color = vec4(0,Plane.normal.x,Plane.point.x,Sphere.x);
}