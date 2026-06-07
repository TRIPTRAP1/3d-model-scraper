#pragma once

#include <d3d11.h>
#include <cstdint>
#include <vector>
#include "camera_params.h"

/**
 * @brief Extracts depth buffer from D3D11 device
 * 
 * The depth buffer contains per-pixel depth information which is essential
 * for reconstructing 3D coordinates from screen pixels.
 */
class DepthBufferExtractor {
public:
    DepthBufferExtractor();
    ~DepthBufferExtractor();
    
    /**
     * @brief Initialize depth buffer extraction
     */
    bool Initialize(ID3D11Device* device, ID3D11DeviceContext* context);
    
    /**
     * @brief Extract depth buffer from current D3D11 state
     * @param depth_out Output buffer for depth values (width * height floats)
     * @param width Output depth buffer width
     * @param height Output depth buffer height
     * @param out_of_range_value Value to use for pixels outside valid range
     * @return true if successful
     */
    bool ExtractDepthBuffer(float* depth_out, uint32_t& width, uint32_t& height,
                           float out_of_range_value = 1.0f);
    
    /**
     * @brief Get the original depth texture
     */
    ID3D11Texture2D* GetDepthTexture() const { return depth_texture_; }

private:
    ID3D11Device* device_ = nullptr;
    ID3D11DeviceContext* context_ = nullptr;
    
    ID3D11Texture2D* depth_texture_ = nullptr;      // Original depth buffer
    ID3D11Texture2D* depth_staging_ = nullptr;      // Staging for CPU readback
    ID3D11Texture2D* depth_converted_ = nullptr;    // Float conversion if needed
    ID3D11Texture2D* depth_converted_staging_ = nullptr;
    
    /**
     * @brief Find the depth stencil view from current render target
     */
    ID3D11DepthStencilView* FindDepthStencilView();
    
    /**
     * @brief Convert depth format to float if necessary
     */
    bool ConvertDepthToFloat(ID3D11Texture2D* source, ID3D11Texture2D* dest);
};
