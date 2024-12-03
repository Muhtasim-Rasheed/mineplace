#version 150

#moj_import <matrix.glsl>

uniform sampler2D Sampler0;
uniform sampler2D Sampler1;

uniform float GameTime;
uniform int EndPortalLayers;

in vec4 texProj0;

const vec3[] COLORS = vec3[](
    vec3(0.094, 0.071, 0.220),
    vec3(0.118, 0.078, 0.255),
    vec3(0.141, 0.086, 0.294),
    vec3(0.169, 0.098, 0.333),
    vec3(0.176, 0.094, 0.310),
    vec3(0.133, 0.075, 0.255),
    vec3(0.169, 0.094, 0.298),
    vec3(0.153, 0.094, 0.278),
    vec3(0.133, 0.075, 0.255),
    vec3(0.141, 0.086, 0.255),
    vec3(0.176, 0.118, 0.318),
    vec3(0.322, 0.118, 0.525),
    vec3(0.447, 0.165, 0.616),
    vec3(0.600, 0.204, 0.690),
    vec3(0.831, 0.259, 0.757),
    vec3(0.906, 0.478, 0.804)
);

const mat4 SCALE_TRANSLATE = mat4(
    0.5, 0.0, 0.0, 0.25,
    0.0, 0.5, 0.0, 0.25,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0
);

mat4 end_portal_layer(float layer) {
    mat4 translate = mat4(
        1.0, 0.0, 0.0, 17.0 / layer,
        0.0, 1.0, 0.0, (2.0 + layer / 1.5) * (GameTime * 5),
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );

    mat2 rotate = mat2_rotate_z(radians((layer * layer * 4321.0 + layer * 9.0) * 2.0));

    mat2 scale = mat2((4.5 - layer / 3.7) * 2.0);

    return mat4(scale * rotate) * translate * SCALE_TRANSLATE;
}

out vec4 fragColor;

void main() {
    
    float angle = GameTime * 40;

    mat2 globalRotate = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));

    vec4 rotatedTexProj0 = texProj0;

    rotatedTexProj0.xy = globalRotate * texProj0.xy;

    vec3 color = textureProj(Sampler0, rotatedTexProj0).rgb * COLORS[0];

    for (int i = 0; i < EndPortalLayers; i++) {
        color += textureProj(Sampler1, rotatedTexProj0 * end_portal_layer(float(i + 1))).rgb * COLORS[i];
    }
    
    fragColor = vec4(color, 1.0);
}

