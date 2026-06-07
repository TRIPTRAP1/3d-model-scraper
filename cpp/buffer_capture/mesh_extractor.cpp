#include "mesh_extractor.h"
#include <algorithm>
#include <unordered_map>
#include <cmath>

CapturedMesh MeshExtractor::ExtractFromD3D11Buffer(
    const void* vertex_data,
    const void* index_data,
    size_t vertex_count,
    size_t index_count,
    size_t vertex_stride) {
    
    CapturedMesh mesh;
    mesh.vertices.reserve(vertex_count);
    mesh.indices.reserve(index_count);
    
    // TODO: Implement vertex extraction based on vertex layout detection
    // This will parse vertex data according to detected format
    
    if (index_data) {
        const uint32_t* indices = reinterpret_cast<const uint32_t*>(index_data);
        for (size_t i = 0; i < index_count; ++i) {
            mesh.indices.push_back(indices[i]);
        }
    }
    
    return mesh;
}

void MeshExtractor::RemoveDuplicateVertices(CapturedMesh& mesh) {
    std::vector<Vertex> unique_vertices;
    std::vector<uint32_t> new_indices;
    std::unordered_map<size_t, uint32_t> vertex_map; // hash -> new index
    
    for (uint32_t idx : mesh.indices) {
        if (idx >= mesh.vertices.size()) continue;
        
        const Vertex& v = mesh.vertices[idx];
        
        // Simple hash based on position
        std::hash<float> hasher;
        size_t vertex_hash = hasher(v.position.x) ^ hasher(v.position.y) ^ hasher(v.position.z);
        
        auto it = vertex_map.find(vertex_hash);
        if (it != vertex_map.end()) {
            new_indices.push_back(it->second);
        } else {
            uint32_t new_idx = static_cast<uint32_t>(unique_vertices.size());
            unique_vertices.push_back(v);
            vertex_map[vertex_hash] = new_idx;
            new_indices.push_back(new_idx);
        }
    }
    
    mesh.vertices = std::move(unique_vertices);
    mesh.indices = std::move(new_indices);
}

void MeshExtractor::CalculateNormals(CapturedMesh& mesh) {
    // Initialize normals to zero
    for (auto& vertex : mesh.vertices) {
        vertex.normal = glm::vec3(0.0f);
    }
    
    // Calculate face normals and accumulate
    for (size_t i = 0; i < mesh.indices.size(); i += 3) {
        if (i + 2 >= mesh.indices.size()) break;
        
        uint32_t i0 = mesh.indices[i];
        uint32_t i1 = mesh.indices[i + 1];
        uint32_t i2 = mesh.indices[i + 2];
        
        if (i0 >= mesh.vertices.size() || i1 >= mesh.vertices.size() || i2 >= mesh.vertices.size()) {
            continue;
        }
        
        Vertex& v0 = mesh.vertices[i0];
        Vertex& v1 = mesh.vertices[i1];
        Vertex& v2 = mesh.vertices[i2];
        
        glm::vec3 edge1 = v1.position - v0.position;
        glm::vec3 edge2 = v2.position - v0.position;
        glm::vec3 face_normal = glm::cross(edge1, edge2);
        
        v0.normal += face_normal;
        v1.normal += face_normal;
        v2.normal += face_normal;
    }
    
    // Normalize
    for (auto& vertex : mesh.vertices) {
        float length = glm::length(vertex.normal);
        if (length > 0.0001f) {
            vertex.normal /= length;
        } else {
            vertex.normal = glm::vec3(0.0f, 1.0f, 0.0f);
        }
    }
}

void MeshExtractor::CalculateTangents(CapturedMesh& mesh) {
    // TODO: Implement tangent calculation using Lengyel's method
    // Tangents are needed for normal mapping
}
