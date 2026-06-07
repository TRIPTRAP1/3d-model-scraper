#pragma once

#include <d3d11.h>
#include <dxgi.h>
#include <memory>
#include <cstdint>
#include "camera_params.h"

/**
 * @brief Manages D3D11 backbuffer hooking and frame capture
 * 
 * Intercepts the D3D11 swapchain to capture the rendered frame
 * along with camera parameters needed for reconstruction
 */
class D3D11BackbufferHook {
public:
    D3D11BackbufferHook();
    ~D3D11BackbufferHook();
    
    /**
     * @brief Initialize the hook on the current D3D11 device
     * @return true if successful
     */
    bool Initialize();
    
    /**
     * @brief Shutdown and unhook
     */
    void Shutdown();
    
    /**
     * @brief Check if hook is active
     */
    bool IsHooked() const { return hooked_; }
    
    /**
     * @brief Capture current backbuffer frame
     * @param rgba_out Output buffer for RGBA pixels (width * height * 4 bytes)
     * @param width Output frame width
     * @param height Output frame height
     * @return true if successful
     */
    bool CaptureBackbuffer(uint8_t* rgba_out, uint32_t& width, uint32_t& height);
    
    /**
     * @brief Get current camera parameters
     */
    const CameraParams& GetCameraParams() const { return camera_params_; }
    
    /**
     * @brief Manually update camera parameters (fallback if auto-detection fails)
     */
    void SetCameraParams(const CameraParams& params) { camera_params_ = params; }

private:
    bool hooked_ = false;
    
    // D3D11 objects
    ID3D11Device* device_ = nullptr;
    ID3D11DeviceContext* device_context_ = nullptr;
    IDXGISwapChain* swap_chain_ = nullptr;
    
    // Staging resources for readback
    ID3D11Texture2D* backbuffer_staging_ = nullptr;
    
    // Camera parameters
    CameraParams camera_params_;
    
    /**
     * @brief Find and hook the D3D11 device/context
     */
    bool FindD3D11Device();
    
    /**
     * @brief Create staging buffers for GPU->CPU transfer
     */
    bool CreateStagingResources(uint32_t width, uint32_t height);
    
    /**
     * @brief Extract camera parameters from D3D11 state
     * 
     * This attempts to infer camera parameters from the D3D11 device's
     * current state. Fallback values used if detection fails.
     */
    void ExtractCameraParameters();
};
