// Simple matrix projection
uniform mat4 projection;

vec4 transform(vec4 position)
{
    return projection*position;
}
