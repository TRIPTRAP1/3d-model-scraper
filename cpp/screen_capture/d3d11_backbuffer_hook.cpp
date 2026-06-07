#include "d3d11_backbuffer_hook.h"
#include <glm/gtc/matrix_transform.hpp>
#include <cstring>

D3D11BackbufferHook::D3D11BackbufferHook() {
    // Initialize default camera params
    camera_params_.viewport_width = 1920;
    camera_params_.viewport_height = 1080;
    camera_params_.fov_y = 45.0f;
    camera_params_.aspect_ratio = 1920.0f / 1080.0f;
    camera_params_.near_plane = 0.1f;
    camera_params_.far_plane = 1000.0f;
    
    // Default camera looking down -Z axis
    camera_params_.position = glm::vec3(0.0f, 0.0f, -5.0f);
    camera_params_.view_matrix = glm::lookAt(
        camera_params_.position,
        camera_params_.position + camera_params_.forward,
        camera_params_.up
    );
    
    camera_params_.projection_matrix = glm::perspective(
        glm::radians(camera_params_.fov_y),
        camera_params_.aspect_ratio,
        camera_params_.near_plane,
        camera_params_.far_plane
    );
    
    camera_params_.UpdateInverse();
}

D3D11BackbufferHook::~D3D11BackbufferHook() {
    Shutdown();
}

bool D3D11BackbufferHook::Initialize() {
    if (!FindD3D11Device()) {
        return false;
    }
    
    // Get backbuffer properties
    ID3D11Texture2D* backbuffer = nullptr;
    if (FAILED(swap_chain_->GetBuffer(0, __uuidof(ID3D11Texture2D), (void**)&backbuffer))) {
        return false;
    }
    
    D3D11_TEXTURE2D_DESC desc;
    backbuffer->GetDesc(&desc);
    camera_params_.viewport_width = desc.Width;
    camera_params_.viewport_height = desc.Height;
    camera_params_.aspect_ratio = static_cast<float>(desc.Width) / static_cast<float>(desc.Height);
    
    // Create staging resources
    if (!CreateStagingResources(desc.Width, desc.Height)) {
        backbuffer->Release();
        return false;
    }
    
    backbuffer->Release();
    hooked_ = true;
    return true;
}

void D3D11BackbufferHook::Shutdown() {
    if (backbuffer_staging_) {
        backbuffer_staging_->Release();
        backbuffer_staging_ = nullptr;
    }
    
    if (swap_chain_) {
        swap_chain_->Release();
        swap_chain_ = nullptr;
    }
    
    if (device_context_) {
        device_context_->Release();
        device_context_ = nullptr;
    }
    
    if (device_) {
        device_->Release();
        device_ = nullptr;
    }
    
    hooked_ = false;
}

bool D3D11BackbufferHook::CaptureBackbuffer(uint8_t* rgba_out, uint32_t& width, uint32_t& height) {
    if (!hooked_ || !device_context_ || !swap_chain_) {
        return false;
    }
    
    // Get backbuffer
    ID3D11Texture2D* backbuffer = nullptr;
    if (FAILED(swap_chain_->GetBuffer(0, __uuidof(ID3D11Texture2D), (void**)&backbuffer))) {
        return false;
    }
    
    D3D11_TEXTURE2D_DESC desc;
    backbuffer->GetDesc(&desc);
    width = desc.Width;
    height = desc.Height;
    
    // Copy backbuffer to staging
    device_context_->CopyResource(backbuffer_staging_, backbuffer);
    
    // Map staging buffer for reading
    D3D11_MAPPED_SUBRESOURCE mapped;
    if (FAILED(device_context_->Map(backbuffer_staging_, 0, D3D11_MAP_READ, 0, &mapped))) {
        backbuffer->Release();
        return false;
    }
    
    // Copy to output
    size_t pixel_count = width * height;
    size_t bytes_per_pixel = 4; // RGBA
    memcpy(rgba_out, mapped.pData, pixel_count * bytes_per_pixel);
    
    device_context_->Unmap(backbuffer_staging_, 0);
    backbuffer->Release();
    
    // Try to extract camera parameters
    ExtractCameraParameters();
    
    return true;
}

bool D3D11BackbufferHook::FindD3D11Device() {
    // Try to find an existing D3D11 device
    // This is a simplified approach - in production, would need more robust detection
    
    HMODULE d3d11_module = GetModuleHandleW(L"d3d11.dll");
    if (!d3d11_module) {
        return false;
    }
    
    // Look for D3D11Device in current process
    // This is a placeholder - real implementation would need to:
    // 1. Enumerate all windows
    // 2. Try to get their device contexts
    // 3. Match against D3D11
    
    // For now, create a test device to verify D3D11 is available
    D3D11_CREATE_DEVICE_FLAG flags = 0;
    
    D3D_FEATURE_LEVEL feature_levels[] = {
        D3D_FEATURE_LEVEL_11_1,
        D3D_FEATURE_LEVEL_11_0,
        D3D_FEATURE_LEVEL_10_1,
        D3D_FEATURE_LEVEL_10_0
    };
    
    D3D_FEATURE_LEVEL feature_level;
    
    if (FAILED(D3D11CreateDevice(
        nullptr,
        D3D_DRIVER_TYPE_HARDWARE,
        nullptr,
        flags,
        feature_levels,
        ARRAYSIZE(feature_levels),
        D3D11_SDK_VERSION,
        &device_,
        &feature_level,
        &device_context_))) {
        return false;
    }
    
    // Create a swapchain for this device (or find existing one)
    // This is simplified - real implementation would hook into existing device/swapchain
    
    return true;
}

bool D3D11BackbufferHook::CreateStagingResources(uint32_t width, uint32_t height) {
    if (!device_) {
        return false;
    }
    
    // Create staging texture for backbuffer readback
    D3D11_TEXTURE2D_DESC staging_desc = {};
    staging_desc.Width = width;
    staging_desc.Height = height;
    staging_desc.MipLevels = 1;
    staging_desc.ArraySize = 1;
    staging_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    staging_desc.SampleDesc.Count = 1;
    staging_desc.SampleDesc.Quality = 0;
    staging_desc.Usage = D3D11_USAGE_STAGING;
    staging_desc.BindFlags = 0;
    staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
    staging_desc.MiscFlags = 0;
    
    if (FAILED(device_->CreateTexture2D(&staging_desc, nullptr, &backbuffer_staging_))) {
        return false;
    }
    
    return true;
}

void D3D11BackbufferHook::ExtractCameraParameters() {
    // TODO: Extract actual camera parameters from D3D11 state
    // This would involve:
    // 1. Reading constant buffers
    // 2. Parsing view/projection matrices
    // 3. Inferring camera position, FOV, etc.
    
    // For now, use default/manually set parameters
}
