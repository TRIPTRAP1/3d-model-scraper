#pragma once

#include <vector>
#include <glm/glm.hpp>

/**
 * @brief Basic mesh data structure
 */
struct Vertex {
    glm::vec3 position;
    glm::vec3 normal = glm::vec3(0.0f, 1.0f, 0.0f);
    glm::vec2 uv = glm::vec2(0.0f);
};

struct Mesh {
    std::vector<Vertex> vertices;
    std::vector<uint32_t> indices;
    
    /**
     * @brief Get total vertex count
     */
    size_t GetVertexCount() const { return vertices.size(); }
    
    /**
     * @brief Get total triangle count
     */
    size_t GetTriangleCount() const { return indices.size() / 3; }
    
    /**
     * @brief Calculate bounds
     */
    void GetBounds(glm::vec3& min_bounds, glm::vec3& max_bounds) const {
        if (vertices.empty()) {
            min_bounds = glm::vec3(0.0f);
            max_bounds = glm::vec3(0.0f);
            return;
        }
        
        min_bounds = vertices[0].position;
        max_bounds = vertices[0].position;
        
        for (const auto& v : vertices) {
            min_bounds = glm::min(min_bounds, v.position);
            max_bounds = glm::max(max_bounds, v.position);
        }
    }
};
