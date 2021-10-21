#version 330

#define CAMERA_POS CameraFrag[3].xyz
#define MAX_STEP StepInfo.x
#define MIN_DIST StepInfo.y
#define SMIN_K 1
#define PI 3.14159265

uniform mat4x4 CameraFrag;
uniform vec4 StepInfo;
uniform vec3 LightPos;

in vec3 v_pixray;
out vec4 f_color;

// Operators

float smin(float a, float b, float k)
{    
    float h = clamp(0.5 + 0.5 * (a - b) / k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

// Distance functions

float sdTorus(vec3 p, vec3 center, vec3 normal, vec3 radii)
{
    vec3 g = dot(p - center, normal) * normal;
    vec3 pp = p - g;
    vec3 m = center + normalize(pp - center) * radii.x;
    return length((p - m)) - radii.y;
}

float sdCone( in vec3 p, in vec2 c, float h )
{
  // c is the sin/cos of the angle, h is height
  // Alternatively pass q instead of (c,h),
  // which is the point at the base in 2D
  vec2 q = h*vec2(c.x/c.y,-1.0);
    
  vec2 w = vec2( length(p.xz), p.y );
  vec2 a = w - q*clamp( dot(w,q)/dot(q,q), 0.0, 1.0 );
  vec2 b = w - q*vec2( clamp( w.x/q.x, 0.0, 1.0 ), 1.0 );
  float k = sign( q.y );
  float d = min(dot( a, a ),dot(b, b));
  float s = max( k*(w.x*q.y-w.y*q.x),k*(w.y-q.y)  );
  return sqrt(d)*sign(s);
}

float sdSphere(vec3 point, float r)
{
    return length(point) - r;
}

float sdPlane(vec3 point, vec4 plane)
{
    vec3 plane_intersect = vec3(0, plane.w, 0);
    return dot (point - plane_intersect, plane.xyz);
}

float sdBox(vec3 point, vec3 side)
{
    vec3 center = vec3(0);    
    vec3 q = abs(point - center) - side;
    float dist =  length(max(q, 0));
    return dist + min(max(q.x,max(q.y,q.z)),0.0);
}

// Modifiers
// None just yet

// Raymarch

float distance(vec3 point)
{
    return max(smin(min(min(min(min(sdSphere(point + vec3(50, 0, 0), 10),sdTorus(point + vec3(20, 0, 0), vec3(0, 0, 0), vec3(0, 0, -1), vec3(10, 2, 0))),sdCone(point, vec2(0.5, 0.8660254037844386), 10)),sdPlane(point, vec4(0, 1, 0, -20))),sdBox(point + vec3(-20, 0, 0), vec3(10, 10, 10))),sdBox(point, vec3(50, 2, 2)), 4),-sdBox(point, vec3(55, 2.2, 2.2)));
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

// Utility

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

// Shadow

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

float shadow(vec3 hit, vec3 hitLightDir, float distToLight)
{
    float step = 0;
    float dist = MAX_STEP;
    float res = 1.0f;
    while (step < distToLight && dist > MIN_DIST)
    {
        dist = distance(hit + hitLightDir * step);
        if (dist < MIN_DIST)
            return 0.0;
        step = step + dist;
    }
    return res;
}

// Main

void main()
{
    vec3 ray = normalize(v_pixray - CAMERA_POS);
    float step = raymarch(CAMERA_POS, ray);

    if (step < MAX_STEP)
    {
        vec3 hit = CAMERA_POS + ray * step;
        vec3 hitToLight = LightPos - hit;
        vec3 hitLightDir = normalize(hitToLight);
        vec3 normal = GetNormal(hit);
        //float shadow = softshadow(hit + MIN_DIST * normal, hitLightDir, length(hitToLight), 10);
        float shadow = shadow(hit + 2 * MIN_DIST * normal, hitLightDir, length(hitToLight));
        
        float diffuse = clamp(dot(hitLightDir, normal), 0, 1);
        vec3 reflect = normalize(2 * dot(hitLightDir, normal) * normal - hitLightDir);
        float specular = clamp(dot(-ray, reflect), 0, 1);
        float shade = diffuse + pow(specular, 7);
        
        //f_color = vec4(shade*hitLightDir, 1);        
        //f_color = vec4(vec3(shade * 60), 1);
        f_color = vec4(shadow * abs(normal) * shade, 1);
        //f_color = vec4(abs(normal), 1);
    }
    else
        f_color = vec4(0,0,0,1);
}