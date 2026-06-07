#pragma once

#include <string>
#include <vector>

struct CapturedMesh;

class OBJExporter {
public:
    /**
     * @brief Export captured mesh to OBJ format
     */
    static bool Export(const CapturedMesh& mesh, const std::string& filepath);
    
    /**
     * @brief Export multiple meshes to OBJ
     */
    static bool ExportMultiple(const std::vector<CapturedMesh>& meshes, const std::string& output_dir);
};
