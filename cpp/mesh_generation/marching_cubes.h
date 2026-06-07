#pragma once

#include <vector>
#include <glm/glm.hpp>
#include "mesh_data.h"

/**
 * @brief Marching Cubes algorithm for converting point cloud to mesh
 * 
 * Takes a point cloud and voxelizes it into a watertight triangle mesh.
 */
class MarchingCubes {
public:
    /**
     * @brief Generate mesh from point cloud using Marching Cubes
     * 
     * @param points Input point cloud
     * @param voxel_size Size of voxels in world units
     * @param out_mesh Output triangle mesh
     * @return true if successful
     */
    static bool GenerateMesh(
        const std::vector<glm::vec3>& points,
        float voxel_size,
        Mesh& out_mesh
    );
    
    /**
     * @brief Generate mesh with additional parameters
     * 
     * @param points Input point cloud
     * @param normals Optional surface normals
     * @param voxel_size Size of voxels
     * @param surface_offset Offset from surface for more closed mesh
     * @param out_mesh Output mesh
     * @return true if successful
     */
    static bool GenerateMeshAdvanced(
        const std::vector<glm::vec3>& points,
        const std::vector<glm::vec3>* normals,
        float voxel_size,
        float surface_offset,
        Mesh& out_mesh
    );
};
