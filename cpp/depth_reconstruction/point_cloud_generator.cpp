#include "point_cloud_generator.h"
#include <algorithm>
#include <unordered_map>
#include <cmath>

size_t PointCloudGenerator::GeneratePointCloud(
    const uint8_t* rgba_buffer,
    const float* depth_buffer,
    uint32_t width,
    uint32_t height,
    const CameraParams& camera,
    std::vector<glm::vec3>& out_points,
    std::vector<glm::vec3>* out_colors,
    float depth_threshold) {
    
    out_points.clear();
    if (out_colors) out_colors->clear();
    
    size_t point_count = 0;
    
    for (uint32_t y = 0; y < height; ++y) {
        for (uint32_t x = 0; x < width; ++x) {
            size_t pixel_idx = y * width + x;
            float depth = depth_buffer[pixel_idx];
            
            // Skip invalid depth values
            if (depth <= depth_threshold || depth >= 1.0f - depth_threshold) {
                continue;
            }
            
            // Convert screen pixel to 3D world coordinate
            glm::vec3 world_pos = camera.ScreenToWorld(
                static_cast<float>(x),
                static_cast<float>(y),
                depth
            );
            
            out_points.push_back(world_pos);
            
            // Extract color if requested
            if (out_colors) {
                size_t color_idx = pixel_idx * 4;
                glm::vec3 color(
                    rgba_buffer[color_idx + 0] / 255.0f,     // R
                    rgba_buffer[color_idx + 1] / 255.0f,     // G
                    rgba_buffer[color_idx + 2] / 255.0f      // B
                );
                out_colors->push_back(color);
            }
            
            point_count++;
        }
    }
    
    return point_count;
}

size_t PointCloudGenerator::DownsamplePointCloud(
    const std::vector<glm::vec3>& points,
    const std::vector<glm::vec3>* colors,
    float grid_size,
    std::vector<glm::vec3>& out_points,
    std::vector<glm::vec3>* out_colors) {
    
    out_points.clear();
    if (out_colors) out_colors->clear();
    
    if (points.empty() || grid_size <= 0.0f) {
        return 0;
    }
    
    // Hash grid for spatial downsampling
    std::unordered_map<uint64_t, std::pair<glm::vec3, glm::vec3>> grid_cells;
    std::unordered_map<uint64_t, uint32_t> cell_counts;
    
    for (size_t i = 0; i < points.size(); ++i) {
        const glm::vec3& p = points[i];
        
        // Compute grid cell coordinates
        int64_t gx = static_cast<int64_t>(std::floor(p.x / grid_size));
        int64_t gy = static_cast<int64_t>(std::floor(p.y / grid_size));
        int64_t gz = static_cast<int64_t>(std::floor(p.z / grid_size));
        
        // Hash coordinates to cell ID
        uint64_t cell_id = ((uint64_t)(gx & 0xFFFFF) << 40) |
                           ((uint64_t)(gy & 0xFFFFF) << 20) |
                           ((uint64_t)(gz & 0xFFFFF));
        
        auto it = grid_cells.find(cell_id);
        if (it == grid_cells.end()) {
            glm::vec3 color = (colors && i < colors->size()) ? (*colors)[i] : glm::vec3(0.5f);
            grid_cells[cell_id] = {p, color};
            cell_counts[cell_id] = 1;
        } else {
            // Average position with existing cell
            it->second.first = (it->second.first * static_cast<float>(cell_counts[cell_id]) + p) /
                              static_cast<float>(cell_counts[cell_id] + 1);
            cell_counts[cell_id]++;
        }
    }
    
    // Extract downsampled points
    for (const auto& cell : grid_cells) {
        out_points.push_back(cell.second.first);
        if (out_colors) {
            out_colors->push_back(cell.second.second);
        }
    }
    
    return out_points.size();
}

void PointCloudGenerator::CalculateNormals(
    const std::vector<glm::vec3>& points,
    uint32_t k,
    std::vector<glm::vec3>& out_normals) {
    
    out_normals.clear();
    out_normals.resize(points.size(), glm::vec3(0.0f));
    
    if (points.size() < k) {
        return;
    }
    
    // Simple normal estimation using k-nearest neighbors
    for (size_t i = 0; i < points.size(); ++i) {
        const glm::vec3& p = points[i];
        
        // Find k nearest neighbors
        std::vector<std::pair<float, size_t>> neighbors;
        
        for (size_t j = 0; j < points.size(); ++j) {
            if (i == j) continue;
            
            float dist_sq = glm::distance2(p, points[j]);
            neighbors.push_back({dist_sq, j});
        }
        
        // Sort by distance
        std::sort(neighbors.begin(), neighbors.end());
        
        // Take k nearest
        neighbors.resize(std::min(static_cast<size_t>(k), neighbors.size()));
        
        // Compute local surface normal using PCA-like approach
        glm::vec3 centroid(0.0f);
        for (const auto& [dist_sq, idx] : neighbors) {
            centroid += points[idx];
        }
        centroid /= static_cast<float>(neighbors.size());
        
        // Compute covariance matrix eigenvalues
        // Simplified: use cross product of first two vectors
        if (neighbors.size() >= 2) {
            glm::vec3 v1 = points[neighbors[0].second] - centroid;
            glm::vec3 v2 = points[neighbors[1].second] - centroid;
            
            glm::vec3 normal = glm::cross(v1, v2);
            float len = glm::length(normal);
            if (len > 0.0001f) {
                out_normals[i] = normal / len;
            }
        }
    }
}
