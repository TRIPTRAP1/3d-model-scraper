#pragma once

#include "../mesh_generation/mesh_data.h"
#include <vector>

/**
 * @brief Post-processing for mesh cleanup and optimization
 * 
 * Ensures mesh is suitable for 3D printing:
 * - Watertight
 * - Manifold
 * - Optimized polygon count
 */
class MeshCleaner {
public:
    /**
     * @brief Remove isolated floating geometry (islands)
     * 
     * Keeps only the largest connected component.
     */
    static void RemoveFloatingIslands(Mesh& mesh);
    
    /**
     * @brief Fill small holes in mesh
     * 
     * Detects open edges and attempts to close them.
     */
    static void FillHoles(Mesh& mesh);
    
    /**
     * @brief Ensure mesh is watertight (no open edges)
     */
    static bool EnsureWatertight(Mesh& mesh);
    
    /**
     * @brief Simplify mesh while preserving shape
     * 
     * @param target_reduction Fraction of vertices to remove (0.0 - 1.0)
     */
    static void SimplifyMesh(Mesh& mesh, float target_reduction = 0.5f);
    
    /**
     * @brief Remove degenerate triangles (zero area)
     */
    static void RemoveDegenerateTriangles(Mesh& mesh);
    
    /**
     * @brief Recalculate vertex normals
     */
    static void RecalculateNormals(Mesh& mesh);
    
    /**
     * @brief Optimize mesh for 3D printing
     * 
     * Applies all necessary cleanups:
     * - Remove islands
     * - Fill holes
     * - Remove degenerates
     * - Ensure watertight
     * - Recalculate normals
     */
    static void OptimizeForPrinting(Mesh& mesh);
};
