#pragma once

#include <vulkan/vulkan.h>
#include <vector>
#include <memory>

class CapturedMesh;

/**
 * @brief Vulkan graphics interception hook
 */
class VulkanHook {
public:
    VulkanHook();
    ~VulkanHook();

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
