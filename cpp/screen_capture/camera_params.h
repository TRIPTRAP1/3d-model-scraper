#pragma once

#include <glm/glm.hpp>

/**
 * @brief Camera parameters needed for screen-to-world reconstruction
 */
struct CameraParams {
    // Projection parameters
    float fov_y = 45.0f;                    // Field of view in degrees (Y-axis)
    float aspect_ratio = 16.0f / 9.0f;      // Width / Height
    float near_plane = 0.1f;                // Near clipping plane
    float far_plane = 1000.0f;              // Far clipping plane
    
    // Matrices
    glm::mat4 view_matrix = glm::mat4(1.0f);           // World to view space
    glm::mat4 projection_matrix = glm::mat4(1.0f);     // View to clip space
    glm::mat4 view_projection = glm::mat4(1.0f);       // Combined
    glm::mat4 view_projection_inverse = glm::mat4(1.0f); // For reconstruction
    
    // Camera position and orientation
    glm::vec3 position = glm::vec3(0.0f);
    glm::vec3 forward = glm::vec3(0.0f, 0.0f, 1.0f);
    glm::vec3 right = glm::vec3(1.0f, 0.0f, 0.0f);
    glm::vec3 up = glm::vec3(0.0f, 1.0f, 0.0f);
    
    // Viewport dimensions
    uint32_t viewport_width = 1920;
    uint32_t viewport_height = 1080;
    
    /**
     * @brief Reconstruct world position from screen coordinates and depth
     * 
     * This is the CORE function for converting screen pixels to 3D coordinates
     */
    glm::vec3 ScreenToWorld(float screen_x, float screen_y, float depth) const {
        // Normalize screen coordinates to [-1, 1]
        float ndc_x = (screen_x / viewport_width) * 2.0f - 1.0f;
        float ndc_y = (screen_y / viewport_height) * 2.0f - 1.0f;
        
        // Depth buffer values are typically in [0, 1]
        // NDC depth is also [-1, 1] in OpenGL, but [0, 1] in D3D
        // We use D3D convention here
        
        // Create clip-space position
        glm::vec4 clip_space = glm::vec4(ndc_x, ndc_y, depth, 1.0f);
        
        // Unproject to world space
        glm::vec4 world_space = view_projection_inverse * clip_space;
        
        // Perspective divide
        if (world_space.w != 0.0f) {
            world_space /= world_space.w;
        }
        
        return glm::vec3(world_space);
    }
    
    /**
     * @brief Recalculate inverse matrix after updating view/projection
     */
    void UpdateInverse() {
        view_projection = projection_matrix * view_matrix;
        view_projection_inverse = glm::inverse(view_projection);
    }
};
