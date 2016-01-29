 #version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec4 position;
// Values that stay constant for the whole mesh.
uniform mat4 Model;
uniform mat4 View;
uniform mat4 Projection;

void main(){
	gl_Position =  Projection * View * Model * position;
}
