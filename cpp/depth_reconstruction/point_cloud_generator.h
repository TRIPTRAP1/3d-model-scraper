#pragma once

#include <vector>
#include <cstdint>
#include <glm/glm.hpp>
#include "../screen_capture/camera_params.h"

/**
 * @brief Converts screen coordinates and depth values to 3D point cloud
 * 
 * This is the core of the screen-to-world transformation.
 * Handles the reconstruction of 3D geometry from screen pixels.
 */
class PointCloudGenerator {
public:
    /**
     * @brief Generate point cloud from screen capture and depth buffer
     * 
     * @param rgba_buffer Screen color buffer (width * height * 4 bytes)
     * @param depth_buffer Depth values per pixel (width * height floats, range [0,1])
     * @param width Screen width in pixels
     * @param height Screen height in pixels
     * @param camera Camera parameters for reconstruction
     * @param out_points Output 3D points (X, Y, Z)
     * @param out_colors Output point colors (R, G, B) - optional
     * @param depth_threshold Only include points within this depth range
     * @return Number of points generated
     */
    static size_t GeneratePointCloud(
        const uint8_t* rgba_buffer,
        const float* depth_buffer,
        uint32_t width,
        uint32_t height,
        const CameraParams& camera,
        std::vector<glm::vec3>& out_points,
        std::vector<glm::vec3>* out_colors = nullptr,
        float depth_threshold = 0.001f
    );
    
    /**
     * @brief Downsample point cloud for faster processing
     * 
     * Uses spatial grid-based downsampling to reduce point count while
     * preserving geometry.
     * 
     * @param points Input points
     * @param colors Optional input colors
     * @param grid_size Size of grid cells for downsampling
     * @param out_points Output downsampled points
     * @param out_colors Output downsampled colors (if provided)
     * @return Number of output points
     */
    static size_t DownsamplePointCloud(
        const std::vector<glm::vec3>& points,
        const std::vector<glm::vec3>* colors,
        float grid_size,
        std::vector<glm::vec3>& out_points,
        std::vector<glm::vec3>* out_colors = nullptr
    );
    
    /**
     * @brief Calculate surface normals for point cloud
     * 
     * Uses k-nearest neighbors to estimate surface normals.
     * 
     * @param points Input point cloud
     * @param k Number of neighbors for normal estimation
     * @param out_normals Output surface normals
     */
    static void CalculateNormals(
        const std::vector<glm::vec3>& points,
        uint32_t k,
        std::vector<glm::vec3>& out_normals
    );
};
