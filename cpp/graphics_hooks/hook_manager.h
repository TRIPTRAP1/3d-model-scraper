#pragma once

#include <memory>
#include <unordered_map>
#include <vector>
#include <string>

class CapturedMesh;
class D3D11Hook;
class D3D12Hook;
class VulkanHook;

/**
 * @brief Central manager for all graphics API hooks
 * 
 * Handles hooking initialization, mesh capture coordination,
 * and inter-hook communication.
 */
class HookManager {
public:
    enum class GraphicsAPI {
        UNKNOWN,
        D3D11,
        D3D12,
        VULKAN,
        OPENGL
    };

    HookManager();
    ~HookManager();

    /**
     * @brief Initialize hooks for detected graphics API
     * @return GraphicsAPI detected and hooked
     */
    GraphicsAPI Initialize();

    /**
     * @brief Shutdown all active hooks
     */
    void Shutdown();

    /**
     * @brief Get all captured meshes from current session
     */
    const std::vector<CapturedMesh>& GetCapturedMeshes() const;

    /**
     * @brief Clear captured mesh buffer
     */
    void ClearCapturedMeshes();

    /**
     * @brief Check if any graphics API is currently hooked
     */
    bool IsHooked() const;

    /**
     * @brief Get currently active graphics API
     */
    GraphicsAPI GetActiveAPI() const { return active_api_; }

    /**
     * @brief Pause/Resume mesh capture
     */
    void SetCaptureEnabled(bool enabled);
    bool IsCaptureEnabled() const { return capture_enabled_; }

private:
    GraphicsAPI active_api_ = GraphicsAPI::UNKNOWN;
    std::unique_ptr<D3D11Hook> d3d11_hook_;
    std::unique_ptr<D3D12Hook> d3d12_hook_;
    std::unique_ptr<VulkanHook> vulkan_hook_;

    std::vector<CapturedMesh> captured_meshes_;
    bool capture_enabled_ = false;

    GraphicsAPI DetectGraphicsAPI();
};
