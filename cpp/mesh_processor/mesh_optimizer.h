#pragma once

#include <string>
#include <vector>

struct CapturedMesh;

class MeshOptimizer {
public:
    /**
     * @brief Optimize mesh for 3D printing/export
     * - Remove internal faces
     * - Fix winding order
     * - Close holes
     * - Simplify geometry
     */
    static void OptimizeForPrinting(CapturedMesh& mesh);
    
    /**
     * @brief Simplify mesh while preserving silhouette
     */
    static void SimplifyMesh(CapturedMesh& mesh, float target_ratio = 0.5f);
    
    /**
     * @brief Merge multiple meshes into one
     */
    static void MergeMeshes(const std::vector<CapturedMesh>& source, CapturedMesh& target);
};
