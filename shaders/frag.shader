#version 450

#define MAX_LIGHTS 10

in vec3 position_worldspace;
in vec2 texture_coord_from_vshader;
in vec3 normal_cameraspace;
in vec3 eyeDirection_cameraspace;
in vec3 lightDirection_cameraspace[MAX_LIGHTS];

out vec4 out_color;

uniform sampler2D texture_sampler;
uniform mat4 Model;
uniform mat4 View;
uniform vec3 lightPosition_worldspace[MAX_LIGHTS];
uniform vec4 lightCone[MAX_LIGHTS]; //x,y,z -> direction; w -> cutoffanglecos (if < 0 then emmits in all directions)
uniform vec4 lightColor[MAX_LIGHTS]; // x,y,z -> color rgb; w -> intensity (if < 0 then does not decay) 
uniform int lightsEnabled[MAX_LIGHTS];

uniform int disableLighting;

uniform vec4 ambient;
uniform vec4 diffuse;
uniform vec4 specular;
uniform vec4 emissive;

uniform float shininess;
uniform float transparency;

void main() {
	if(disableLighting == 1){
		out_color = texture(texture_sampler, texture_coord_from_vshader);
		out_color.a -= transparency;
		return;
	}

	//Material properties
	vec3 matDiffuse = (texture(texture_sampler, texture_coord_from_vshader).rgb * diffuse.xyz);
	vec3 ambientCoef = ambient.xyz / vec3(255, 255, 255);
	vec3 matAmbient = ambientCoef * matDiffuse;
	vec3 matSpecular = specular.xyz;

	out_color.rgb = vec3(0,0,0);//Very important! start with black

	vec3 n = normalize( normal_cameraspace );
	vec3 E = normalize(eyeDirection_cameraspace);

	vec3 light_color_sum = vec3(0,0,0);
	for(int i=0; i<MAX_LIGHTS; i++){
		if(lightsEnabled[i] == 1){
			vec3 lightDirection_worldspace = lightPosition_worldspace[i].xyz - position_worldspace; 
			float distance_to_light = length( lightDirection_worldspace );

			vec3 l = normalize( lightDirection_cameraspace[i] );

			float spotEffect = dot( normalize(lightCone[i].xyz), normalize(-lightDirection_worldspace) );
			if(spotEffect > lightCone[i].w || lightCone[i].w <= 0){

				vec3 R = reflect(-l, n);
				float cosAlpha = clamp( dot(E,R), 0,1);
				float cosTheta = clamp( dot(n,l), 0,1);

				float decay;
				if(lightColor[i].w <= 0)
					decay = 1;
				else
					decay = (distance_to_light*distance_to_light/2);

				light_color_sum += matDiffuse * lightColor[i].xyz * abs(lightColor[i].w) * cosTheta / decay +
					matSpecular * (shininess/16.0) * lightColor[i].xyz * abs(lightColor[i].w) * pow(cosAlpha, 5) / decay;
			}
		}
		
	}
	out_color.rgb = matAmbient + emissive.xyz + light_color_sum;
	out_color.a = texture(texture_sampler, texture_coord_from_vshader).a - transparency;
}
