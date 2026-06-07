#pragma once

#include <string>
#include <vector>

struct CapturedMesh;

class STLExporter {
public:
    /**
     * @brief Export to STL format (ASCII or Binary)
     */
    static bool ExportASCII(const CapturedMesh& mesh, const std::string& filepath);
    static bool ExportBinary(const CapturedMesh& mesh, const std::string& filepath);
};
