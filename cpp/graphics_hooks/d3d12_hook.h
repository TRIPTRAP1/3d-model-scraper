#pragma once

#include <d3d12.h>
#include <vector>
#include <memory>

class CapturedMesh;

/**
 * @brief Direct3D 12 graphics interception hook
 */
class D3D12Hook {
public:
    D3D12Hook();
    ~D3D12Hook();

    bool Initialize();
    void Shutdown();
    bool IsHooked() const { return hooked_; }
    void CaptureNextDraw();
    const std::vector<CapturedMesh>& GetCapturedMeshes() const { return captured_meshes_; }
    void ClearCapturedMeshes() { captured_meshes_.clear(); }

private:
    bool hooked_ = false;
    std::vector<CapturedMesh> captured_meshes_;
};
