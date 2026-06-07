#pragma once

#include <string>
#include <vector>

struct CapturedMesh;

class GLBExporter {
public:
    /**
     * @brief Export to GLB (binary GLTF) format with embedded textures
     */
    static bool Export(const CapturedMesh& mesh, const std::string& filepath);
    
    static bool ExportMultiple(const std::vector<CapturedMesh>& meshes, const std::string& filepath);
};
