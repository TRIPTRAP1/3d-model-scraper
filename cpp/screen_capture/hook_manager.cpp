#include "hook_manager.h"

ScreenCaptureManager::ScreenCaptureManager() {}

ScreenCaptureManager::~ScreenCaptureManager() {
    Shutdown();
}

bool ScreenCaptureManager::Initialize() {
    backbuffer_hook_ = std::make_unique<D3D11BackbufferHook>();
    if (!backbuffer_hook_->Initialize()) {
        return false;
    }
    
    // TODO: Initialize depth extractor with device from backbuffer hook
    // This will need to expose device/context from D3D11BackbufferHook
    
    return true;
}

void ScreenCaptureManager::Shutdown() {
    if (backbuffer_hook_) {
        backbuffer_hook_->Shutdown();
        backbuffer_hook_.reset();
    }
    
    if (depth_extractor_) {
        depth_extractor_.reset();
    }
}

bool ScreenCaptureManager::CaptureFrame(uint8_t* rgba_out, float* depth_out,
                                        uint32_t& width, uint32_t& height) {
    if (!IsReady()) {
        return false;
    }
    
    // Capture backbuffer (RGBA)
    if (!backbuffer_hook_->CaptureBackbuffer(rgba_out, width, height)) {
        return false;
    }
    
    // Capture depth buffer
    uint32_t depth_width, depth_height;
    if (depth_extractor_ && !depth_extractor_->ExtractDepthBuffer(depth_out, depth_width, depth_height)) {
        // Depth extraction failed, but continue with just color
        // Fill depth with default values
        for (size_t i = 0; i < width * height; ++i) {
            depth_out[i] = 1.0f; // Far plane
        }
    }
    
    return true;
}

const CameraParams& ScreenCaptureManager::GetCameraParams() const {
    return backbuffer_hook_->GetCameraParams();
}

void ScreenCaptureManager::SetCameraParams(const CameraParams& params) {
    backbuffer_hook_->SetCameraParams(params);
}
