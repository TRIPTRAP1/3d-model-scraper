#pragma once

#include <vector>
#include <string>
#include <glm/glm.hpp>

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
    glm::vec2 uv;
    glm::vec4 color = glm::vec4(1.0f);
    glm::vec4 bone_weights = glm::vec4(0.0f);
    glm::ivec4 bone_indices = glm::ivec4(0);
};

struct Material {
    std::string name;
    glm::vec4 diffuse_color = glm::vec4(1.0f);
    glm::vec4 specular_color = glm::vec4(1.0f);
    float roughness = 0.5f;
    float metallic = 0.0f;
    
    std::string diffuse_texture;
    std::string normal_texture;
    std::string specular_texture;
    std::string roughness_texture;
};

struct Bone {
    std::string name;
    int parent_index = -1;
    glm::mat4 bind_pose;
};

struct CapturedMesh {
    std::string name;
    std::vector<Vertex> vertices;
    std::vector<uint32_t> indices;
    std::vector<Material> materials;
    std::vector<Bone> bones;
    
    glm::mat4 world_matrix = glm::mat4(1.0f);
    
    uint64_t capture_time = 0;
    uint32_t draw_call_count = 0;
};

class MeshExtractor {
public:
    static CapturedMesh ExtractFromD3D11Buffer(
        const void* vertex_data,
        const void* index_data,
        size_t vertex_count,
        size_t index_count,
        size_t vertex_stride
    );

    static void RemoveDuplicateVertices(CapturedMesh& mesh);
    static void CalculateNormals(CapturedMesh& mesh);
    static void CalculateTangents(CapturedMesh& mesh);
};
