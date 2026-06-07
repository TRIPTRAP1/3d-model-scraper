#include "depth_buffer_extractor.h"
#include <cstring>

DepthBufferExtractor::DepthBufferExtractor() {}

DepthBufferExtractor::~DepthBufferExtractor() {
    if (depth_staging_) depth_staging_->Release();
    if (depth_converted_) depth_converted_->Release();
    if (depth_converted_staging_) depth_converted_staging_->Release();
    if (depth_texture_) depth_texture_->Release();
}

bool DepthBufferExtractor::Initialize(ID3D11Device* device, ID3D11DeviceContext* context) {
    if (!device || !context) return false;
    
    device_ = device;
    context_ = context;
    
    return true;
}

bool DepthBufferExtractor::ExtractDepthBuffer(float* depth_out, uint32_t& width, uint32_t& height,
                                             float out_of_range_value) {
    if (!device_ || !context_) {
        return false;
    }
    
    // Get current output merger state to find depth buffer
    ID3D11RenderTargetView* rtv = nullptr;
    ID3D11DepthStencilView* dsv = nullptr;
    
    context_->OMGetRenderTargets(1, &rtv, &dsv);
    
    if (!dsv) {
        if (rtv) rtv->Release();
        return false;
    }
    
    // Get resource from depth stencil view
    ID3D11Resource* resource = nullptr;
    dsv->GetResource(&resource);
    
    // Query as texture
    ID3D11Texture2D* depth_texture = nullptr;
    if (FAILED(resource->QueryInterface(__uuidof(ID3D11Texture2D), (void**)&depth_texture))) {
        resource->Release();
        dsv->Release();
        if (rtv) rtv->Release();
        return false;
    }
    
    D3D11_TEXTURE2D_DESC desc;
    depth_texture->GetDesc(&desc);
    width = desc.Width;
    height = desc.Height;
    
    // Create staging texture if not exists or size changed
    if (!depth_staging_ || 
        (depth_staging_ && 
         ([&]() {
             D3D11_TEXTURE2D_DESC staging_desc;
             depth_staging_->GetDesc(&staging_desc);
             return staging_desc.Width != width || staging_desc.Height != height;
         })()))
    {
        if (depth_staging_) depth_staging_->Release();
        
        D3D11_TEXTURE2D_DESC staging_desc = desc;
        staging_desc.Usage = D3D11_USAGE_STAGING;
        staging_desc.BindFlags = 0;
        staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        staging_desc.MiscFlags = 0;
        
        if (FAILED(device_->CreateTexture2D(&staging_desc, nullptr, &depth_staging_))) {
            depth_texture->Release();
            resource->Release();
            dsv->Release();
            if (rtv) rtv->Release();
            return false;
        }
    }
    
    // Copy depth buffer to staging
    context_->CopyResource(depth_staging_, depth_texture);
    
    // Map and read depth data
    D3D11_MAPPED_SUBRESOURCE mapped;
    if (FAILED(context_->Map(depth_staging_, 0, D3D11_MAP_READ, 0, &mapped))) {
        depth_texture->Release();
        resource->Release();
        dsv->Release();
        if (rtv) rtv->Release();
        return false;
    }
    
    // Convert depth values to floats
    size_t pixel_count = width * height;
    
    switch (desc.Format) {
        case DXGI_FORMAT_D32_FLOAT:
            // Direct copy - already float
            memcpy(depth_out, mapped.pData, pixel_count * sizeof(float));
            break;
            
        case DXGI_FORMAT_D24_UNORM_S8_UINT:
            // Extract depth from 24-bit value
            for (size_t i = 0; i < pixel_count; ++i) {
                uint32_t packed = ((uint32_t*)mapped.pData)[i];
                uint32_t depth24 = (packed >> 8) & 0xFFFFFF;
                depth_out[i] = static_cast<float>(depth24) / 16777215.0f; // 2^24 - 1
            }
            break;
            
        case DXGI_FORMAT_D16_UNORM:
            // Convert 16-bit depth
            for (size_t i = 0; i < pixel_count; ++i) {
                uint16_t depth16 = ((uint16_t*)mapped.pData)[i];
                depth_out[i] = static_cast<float>(depth16) / 65535.0f; // 2^16 - 1
            }
            break;
            
        case DXGI_FORMAT_D32_FLOAT_S8X24_UINT:
            // First 32 bits are float depth
            for (size_t i = 0; i < pixel_count; ++i) {
                depth_out[i] = ((float*)mapped.pData)[i * 2]; // Every other float is depth
            }
            break;
            
        default:
            // Unknown format - use out of range value
            for (size_t i = 0; i < pixel_count; ++i) {
                depth_out[i] = out_of_range_value;
            }
            break;
    }
    
    context_->Unmap(depth_staging_, 0);
    
    depth_texture->Release();
    resource->Release();
    dsv->Release();
    if (rtv) rtv->Release();
    
    return true;
}

ID3D11DepthStencilView* DepthBufferExtractor::FindDepthStencilView() {
    if (!context_) return nullptr;
    
    ID3D11RenderTargetView* rtv = nullptr;
    ID3D11DepthStencilView* dsv = nullptr;
    
    context_->OMGetRenderTargets(1, &rtv, &dsv);
    
    if (rtv) rtv->Release();
    
    return dsv;
}

bool DepthBufferExtractor::ConvertDepthToFloat(ID3D11Texture2D* source, ID3D11Texture2D* dest) {
    // TODO: Implement depth format conversion compute shader if needed
    return true;
}
