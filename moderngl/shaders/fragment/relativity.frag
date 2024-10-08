#version 460

//comment this if you do not want the delayed view.
#define RETARD 1.

#define MAX_ITER 1500.
#define MAX_DIST 70.
#define SURF .0001

uniform mat4x4 transformMatrix;
uniform vec4 fourvel;
uniform vec4 uposition;
uniform vec4 boost;
uniform vec3 orientation;
uniform vec3 iResolution;
uniform vec3 iMouse;
uniform float iTimeDelta;

vec4 position;

in vec3 v_pixray;
in vec2 fragCoord;
out vec4 f_color;

vec3 SIZE= vec3(.1); 

//ray origin in the moving coords.
vec4 RO, rd;
vec2 m;

vec3 col = vec3(0);

float halo=0.;
float cylinder;   
float cylinder2; 
float cylinder3;
float cylinder4;

###include "common"

vec3 color( float s){
    return vec3(1) - vec3(1.,1.,0)*smoothstep(.0,1., s)-
            vec3(0.,.6,.6)*smoothstep(0.,1., -s);
}

void updateVel(){
    col.x = iTimeDelta;
    // Fetch the fourvelocity from the Buffer A
    //boost= texelFetch( iChannel0, ivec2(5,5), 0);
    //orientation=texelFetch( iChannel0, ivec2(6,6), 0).xyz;
    //fourvel=texelFetch( iChannel0, ivec2(0,0), 0 );
}

void updatePos(){
    // Fetch the fourposition from the Buffer B
    
    //position =texelFetch( iChannel0, ivec2(1,0), 0 );
    position = uposition;
    vec4 cam=vec4(-1,0,0,0);
    if(m!=vec2(0)){
        cam.xy*=rot((m.y-.5)*PI);
        cam.xz*=rot(-(m.x-.5)*2.*PI);    
    }
    position+=transformMatrix*cam;
}


float sdBox(vec4 p , vec3 s){
    float time=p.w;
    p.xyz=fract(p.xyz)-.5; //this creates the grid of reference cubes
    p.yz*=rot(p.w*.5);
    p.xyz= abs(p.xyz)-s;
    return length(max(p.xyz,0.))+ min(max(p.x,max(p.y,p.z)),0.);  
}

float sdCylinder( vec3 p, vec2 h )
{
    vec2 d = abs(vec2(length(p.xz),p.y)) - h;
    float outer= min(max(d.x,d.y),0.0) + length(max(d,0.0));
    vec2 d2 = abs(vec2(length(p.xz),p.y)) - (h+vec2(-.05,.05));
    float inner= min(max(d2.x,d2.y),0.0) + length(max(d2,0.0));
    
    return max(outer,-inner);
}


float getDist(vec4 q)
{
    float dist= sdBox(q,SIZE);
    
    //the cylinders:
    float len= 3.;
    float d= 4.;
    float s=.5;
    q.x-=d;
    cylinder= sdCylinder(q.zxy, vec2(s,len*s));
    q.x+=2.*d;
    cylinder2= sdCylinder(q.zxy, vec2(s,len*s));
    q.x-=d;
    q.z-=d;
    cylinder3= sdCylinder(q.xzy, vec2(s,len*s));
    q.z+=2.*d;
    cylinder4= sdCylinder(q.xzy, vec2(s,len*s));
    
    dist = min(dist,cylinder);
    dist = min(dist,cylinder2);
    dist = min(dist,cylinder3);
    dist = min(dist,cylinder4);
    
    return dist;
}



vec4 getRayDir(vec2 uv, vec4 lookAt, float zoom)
{

    vec3 f= normalize(lookAt.xyz);
    vec3 r= normalize(cross(vec3(0,1,0),f));
    vec3 u= cross(f,r);
    
    return vec4(normalize(f*zoom+uv.x*r+uv.y*u),lookAt.w/c);

    //the w-component determines how we look into past/future/present.
}

float RayMarch(vec4 ro, vec4 rd, float side)
{
    float dO=0.;
    float i=0.;
   while(i<MAX_ITER){
      vec4 p= ro+dO*rd; //if rd.w =-c we look back in time as we march further away
      
      float dS=side*getDist(p); 
        
      dO+=dS;
  
      if(dO>MAX_DIST||dS<SURF){
          break;
      }
      i++;
    } 
    
      return dO;
}

vec3 getNormal(vec4 p)
{
   vec2 e= vec2(0.01,0);
   float d=getDist(p);
   vec3 n = d-vec3(getDist(p- e.xyyy),getDist(p- e.yxyy),getDist(p- e.yyxy));
   
   return normalize(n);
}

void getMaterial(vec4 p)
{
    if(cylinder<5.*SURF)
    {
        p.yz*=rot(p.w*.5);
        col=vec3(2,0,.2)*sin(atan(p.y,p.z)*10.)*sin(atan(p.y,p.z)*10.);
    }
    else if(cylinder2<5.*SURF)
    {
        p.yz*=rot(p.w*.5);
        col=vec3(.2,1,0)*sin(atan(p.y,p.z)*10.)*sin(atan(p.y,p.z)*10.);
    }
    else if(cylinder3<5.*SURF)
    {
        p.xy*=rot(p.w*.5);
        col=vec3(1,0,1)*sin(atan(p.y,p.x)*10.)*sin(atan(p.y,p.x)*10.);
    }
    else if (cylinder4<5.*SURF)
    {
        p.xy*=rot(p.w*.5);
        col=vec3(0,.2,1)*sin(atan(p.y,p.x)*10.)*sin(atan(p.y,p.x)*10.);;
    }// else col= vec3(1);
}


void angularRepeat(const float a, inout vec2 v)
{
    float an = atan(v.y,v.x);
    float len = length(v);
    an = mod(an+a*.5,a)-a*.5;
    v = vec2(cos(an),sin(an))*len;
}

void angularRepeat(const float a, const float offset, inout vec2 v)
{
    float an = atan(v.y,v.x);
    float len = length(v);
    an = mod(an+a*.5,a)-a*.5;
    an+=offset;
    v = vec2(cos(an),sin(an))*len;
}

float mBox(vec3 p, vec3 b)
{
	return max(max(abs(p.x)-b.x,abs(p.y)-b.y),abs(p.z)-b.z);
}

###include "rocket"

#define C(c) U.x-=.5; O+= Char(U,c)

vec4 Char(vec2 p, int c) 
{
    if (p.x<.0|| p.x>1. || p.y<0.|| p.y>1.) return vec4(0,0,0,1e5);
	return vec4(1.0f);//textureGrad( iChannel2, p/16. + fract( vec2(c, 15-c/16) / 16. ), dFdx(p/16.),dFdy(p/16.) );
}

vec4 text( out vec4 O, vec2 uv )
{
    return vec4(1.0f);
//     O = vec4(0.0);
//     uv /= iResolution.y;
//     vec2 pos = vec2(.0,.9);
//     float FontSize = 6.;
//     vec2 U = ( uv - pos)*64.0/FontSize;
   
 
//    float k =abs(fourvel.x/fourvel.w);
//    C(115);C(112);C(101);C(101);C(100);C(32);
   
  
//    C(46);
//    C(48+int(10.*fract(k)));
//    C(48+int(10.*fract(10.*k))); C(99);
   
   
//    U.y+=1.1; U.x+=5.;
//    C(116);C(105);C(109);C(101);C(32);
//    C(44-int(sign(position.w)));
   
//    C(48+int(10.*fract(abs(position.w*.01))));
//    C(48+int(10.*fract(abs(position.w*.1))));
//    C(46);
//    C(48+int(10.*fract(abs(position.w))));
//    return O.xxxx;
}


// include "bufferb"

void main()
{
    vec2 uv = (fragCoord-.5*iResolution.xy)/iResolution.y;
    
    if(iMouse.xy==vec2(0))
         m = vec2(.5);
    else{
        m = (iMouse.xy-.5)/iResolution.xy;
    } 

    updateVel();    
    updatePos();
    
    //ray's spacetime origin represented in "stationary coordinates":
    RO=position;
    float zoom= 1.;
    
    //four-direction in our moving coords:
    vec4 lookAt;
    //what we actually see as light reaches our eyes:
    #ifdef RETARD 
        lookAt = vec4(c, 0, 0, -1);
    #else //the "instantaneous geometry" of spacetime/coordinates: 
        lookAt = vec4(c, 0, 0, 0);
     #endif
     
    if(m!=vec2(0)){
        lookAt.xy*=rot((m.y-.5)*PI);
        lookAt.xz*=rot(-(m.x-.5)*2.*PI);
    }
      
    //ray in our moving coords:
    vec4 ray= getRayDir(uv, lookAt, zoom);
    
    
    //adding the rocket on top
    vec3 r_color = vec3 (0);
    vec3 cam=vec3(-7,1.5,0);
    
    if(m!=vec2(.5)){
        cam.xy*=rot((m.y-.5)*PI);
        cam.xz*=rot(-(m.x-.5)*2.*PI);        
    }           
    rocket (r_color, cam, ray.xyz);
    
    if (length (r_color) > 0.0) {
        f_color.xyz = r_color;
    }else{ 
    
    
    
    //ray direction from moving coords to stationary coords:
    rd= transformMatrix*ray; 
    //some rescaling for accuracy:
    
    #ifdef RETARD
        rd.xyz=normalize(rd.xyz);
        rd.w=-RETARD;
    #else
       rd=normalize(rd); 
    #endif    
    
   /* //just some helpfull scaling factors for raymarching:
    if(RETARD>0.){
         vv= max(0., -dot(fourvel.xyzw, rd.xyzw));
    }else{
         vv= abs(dot(fourvel.xyzw, rd.xyzw));
    }
    */
    
    
    //RAYMARCH IN SPACETIME calculated in stationary coordinates:
    vec4 p=RO;          
    
    float d= RayMarch(p, rd, 1.);
    
    
     if(d<MAX_DIST){ //if we hit an object:
          p= p+ d*rd;
          
          col=color(dot(normalize(rd.xyz), fourvel.xyz));
          getMaterial(p);

          vec3 n= getNormal(p);
      
          float dif= dot(n, normalize(vec3(-3,2,1)))*.5+.5;
          col/=length(d*rd)*.2;
          col*=dif*dif;            
      
    }

    //col.xyz+=text(f_color, fragCoord).xyz;


    f_color = vec4(col,1.0)+halo*halo*vec4(.4,.2,1,1);
    
   }

}