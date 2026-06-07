#include "mesh_cleaner.h"
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <queue>

void MeshCleaner::RemoveFloatingIslands(Mesh& mesh) {
    if (mesh.indices.empty()) return;
    
    uint32_t vertex_count = static_cast<uint32_t>(mesh.vertices.size());
    
    // Build adjacency graph
    std::vector<std::vector<uint32_t>> adjacency(vertex_count);
    for (size_t i = 0; i < mesh.indices.size(); i += 3) {
        uint32_t i0 = mesh.indices[i];
        uint32_t i1 = mesh.indices[i + 1];
        uint32_t i2 = mesh.indices[i + 2];
        
        adjacency[i0].push_back(i1);
        adjacency[i0].push_back(i2);
        adjacency[i1].push_back(i0);
        adjacency[i1].push_back(i2);
        adjacency[i2].push_back(i0);
        adjacency[i2].push_back(i1);
    }
    
    // Find connected components using BFS
    std::vector<bool> visited(vertex_count, false);
    std::vector<std::vector<uint32_t>> components;
    
    for (uint32_t start = 0; start < vertex_count; ++start) {
        if (visited[start]) continue;
        
        std::vector<uint32_t> component;
        std::queue<uint32_t> q;
        q.push(start);
        visited[start] = true;
        
        while (!q.empty()) {
            uint32_t v = q.front();
            q.pop();
            component.push_back(v);
            
            for (uint32_t neighbor : adjacency[v]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    q.push(neighbor);
                }
            }
        }
        
        if (!component.empty()) {
            components.push_back(component);
        }
    }
    
    // Keep only largest component
    if (components.size() <= 1) return;
    
    size_t largest_idx = 0;
    size_t largest_size = components[0].size();
    
    for (size_t i = 1; i < components.size(); ++i) {
        if (components[i].size() > largest_size) {
            largest_size = components[i].size();
            largest_idx = i;
        }
    }
    
    // Mark vertices to keep
    std::unordered_set<uint32_t> keep_vertices(components[largest_idx].begin(),
                                               components[largest_idx].end());
    
    // Remove triangles with vertices outside largest component
    std::vector<uint32_t> new_indices;
    for (size_t i = 0; i < mesh.indices.size(); i += 3) {
        uint32_t i0 = mesh.indices[i];
        uint32_t i1 = mesh.indices[i + 1];
        uint32_t i2 = mesh.indices[i + 2];
        
        if (keep_vertices.count(i0) && keep_vertices.count(i1) && keep_vertices.count(i2)) {
            new_indices.push_back(i0);
            new_indices.push_back(i1);
            new_indices.push_back(i2);
        }
    }
    
    mesh.indices = new_indices;
}

void MeshCleaner::FillHoles(Mesh& mesh) {
    // TODO: Implement hole filling algorithm
    // Options: simple fan triangulation, or more sophisticated methods
}

bool MeshCleaner::EnsureWatertight(Mesh& mesh) {
    // TODO: Verify mesh is watertight (no open edges)
    return true;
}

void MeshCleaner::SimplifyMesh(Mesh& mesh, float target_reduction) {
    // TODO: Implement mesh simplification
    // Could use quadric error metrics or other simplification algorithms
}

void MeshCleaner::RemoveDegenerateTriangles(Mesh& mesh) {
    std::vector<uint32_t> new_indices;
    
    const float MIN_AREA = 1e-6f;
    
    for (size_t i = 0; i < mesh.indices.size(); i += 3) {
        uint32_t i0 = mesh.indices[i];
        uint32_t i1 = mesh.indices[i + 1];
        uint32_t i2 = mesh.indices[i + 2];
        
        if (i0 >= mesh.vertices.size() || i1 >= mesh.vertices.size() || i2 >= mesh.vertices.size()) {
            continue;
        }
        
        const glm::vec3& p0 = mesh.vertices[i0].position;
        const glm::vec3& p1 = mesh.vertices[i1].position;
        const glm::vec3& p2 = mesh.vertices[i2].position;
        
        // Calculate triangle area using cross product
        glm::vec3 edge1 = p1 - p0;
        glm::vec3 edge2 = p2 - p0;
        float area = glm::length(glm::cross(edge1, edge2)) * 0.5f;
        
        if (area > MIN_AREA) {
            new_indices.push_back(i0);
            new_indices.push_back(i1);
            new_indices.push_back(i2);
        }
    }
    
    mesh.indices = new_indices;
}

void MeshCleaner::RecalculateNormals(Mesh& mesh) {
    // Initialize normals to zero
    for (auto& v : mesh.vertices) {
        v.normal = glm::vec3(0.0f);
    }
    
    // Accumulate face normals
    for (size_t i = 0; i < mesh.indices.size(); i += 3) {
        uint32_t i0 = mesh.indices[i];
        uint32_t i1 = mesh.indices[i + 1];
        uint32_t i2 = mesh.indices[i + 2];
        
        if (i0 >= mesh.vertices.size() || i1 >= mesh.vertices.size() || i2 >= mesh.vertices.size()) {
            continue;
        }
        
        const glm::vec3& p0 = mesh.vertices[i0].position;
        const glm::vec3& p1 = mesh.vertices[i1].position;
        const glm::vec3& p2 = mesh.vertices[i2].position;
        
        glm::vec3 edge1 = p1 - p0;
        glm::vec3 edge2 = p2 - p0;
        glm::vec3 face_normal = glm::cross(edge1, edge2);
        
        mesh.vertices[i0].normal += face_normal;
        mesh.vertices[i1].normal += face_normal;
        mesh.vertices[i2].normal += face_normal;
    }
    
    // Normalize
    for (auto& v : mesh.vertices) {
        float len = glm::length(v.normal);
        if (len > 1e-6f) {
            v.normal /= len;
        } else {
            v.normal = glm::vec3(0.0f, 1.0f, 0.0f);
        }
    }
}

void MeshCleaner::OptimizeForPrinting(Mesh& mesh) {
    RemoveDegenerateTriangles(mesh);
    RemoveFloatingIslands(mesh);
    FillHoles(mesh);
    EnsureWatertight(mesh);
    RecalculateNormals(mesh);
}
