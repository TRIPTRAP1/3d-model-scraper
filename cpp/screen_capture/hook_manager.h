#pragma once

#include <memory>
#include "d3d11_backbuffer_hook.h"
#include "depth_buffer_extractor.h"
#include "camera_params.h"
#include <cstdint>

/**
 * @brief Manages screen capture and depth extraction
 * 
 * Single point of contact for all screen capture operations.
 * Handles backbuffer and depth buffer extraction, coordinate transformation.
 */
class ScreenCaptureManager {
public:
    ScreenCaptureManager();
    ~ScreenCaptureManager();
    
    /**
     * @brief Initialize screen capture system
     * @return true if successful
     */
    bool Initialize();
    
    /**
     * @brief Shutdown screen capture
     */
    void Shutdown();
    
    /**
     * @brief Capture current frame (color + depth)
     * @param rgba_out Output buffer for RGBA pixels (width * height * 4)
     * @param depth_out Output buffer for depth values (width * height * 4)
     * @param width Output frame width
     * @param height Output frame height
     * @return true if successful
     */
    bool CaptureFrame(uint8_t* rgba_out, float* depth_out,
                      uint32_t& width, uint32_t& height);
    
    /**
     * @brief Get camera parameters for current frame
     */
    const CameraParams& GetCameraParams() const;
    
    /**
     * @brief Manually set camera parameters (for testing/fallback)
     */
    void SetCameraParams(const CameraParams& params);
    
    /**
     * @brief Check if capture system is ready
     */
    bool IsReady() const { return backbuffer_hook_ && backbuffer_hook_->IsHooked(); }

private:
    std::unique_ptr<D3D11BackbufferHook> backbuffer_hook_;
    std::unique_ptr<DepthBufferExtractor> depth_extractor_;
};
