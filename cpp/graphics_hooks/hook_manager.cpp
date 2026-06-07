#include "hook_manager.h"
#include "d3d11_hook.h"
#include "d3d12_hook.h"
#include "vulkan_hook.h"

HookManager::HookManager() {}

HookManager::~HookManager() {
    Shutdown();
}

HookManager::GraphicsAPI HookManager::Initialize() {
    active_api_ = DetectGraphicsAPI();

    switch (active_api_) {
        case GraphicsAPI::D3D11:
            d3d11_hook_ = std::make_unique<D3D11Hook>();
            if (d3d11_hook_->Initialize()) {
                return GraphicsAPI::D3D11;
            }
            break;

        case GraphicsAPI::D3D12:
            d3d12_hook_ = std::make_unique<D3D12Hook>();
            if (d3d12_hook_->Initialize()) {
                return GraphicsAPI::D3D12;
            }
            break;

        case GraphicsAPI::VULKAN:
            vulkan_hook_ = std::make_unique<VulkanHook>();
            if (vulkan_hook_->Initialize()) {
                return GraphicsAPI::VULKAN;
            }
            break;

        default:
            active_api_ = GraphicsAPI::UNKNOWN;
            break;
    }

    return GraphicsAPI::UNKNOWN;
}

void HookManager::Shutdown() {
    if (d3d11_hook_) {
        d3d11_hook_->Shutdown();
        d3d11_hook_.reset();
    }
    if (d3d12_hook_) {
        d3d12_hook_->Shutdown();
        d3d12_hook_.reset();
    }
    if (vulkan_hook_) {
        vulkan_hook_->Shutdown();
        vulkan_hook_.reset();
    }
    active_api_ = GraphicsAPI::UNKNOWN;
}

const std::vector<CapturedMesh>& HookManager::GetCapturedMeshes() const {
    return captured_meshes_;
}

void HookManager::ClearCapturedMeshes() {
    captured_meshes_.clear();
}

bool HookManager::IsHooked() const {
    switch (active_api_) {
        case GraphicsAPI::D3D11:
            return d3d11_hook_ && d3d11_hook_->IsHooked();
        case GraphicsAPI::D3D12:
            return d3d12_hook_ && d3d12_hook_->IsHooked();
        case GraphicsAPI::VULKAN:
            return vulkan_hook_ && vulkan_hook_->IsHooked();
        default:
            return false;
    }
}

void HookManager::SetCaptureEnabled(bool enabled) {
    capture_enabled_ = enabled;
    if (d3d11_hook_ && d3d11_hook_->IsHooked()) {
        // Implement capture enable/disable logic
    }
}

HookManager::GraphicsAPI HookManager::DetectGraphicsAPI() {
    // TODO: Detect which graphics API is in use
    // Priority: D3D11 > D3D12 > Vulkan > OpenGL
    
    // Check for D3D11 module
    if (GetModuleHandle(L"d3d11.dll")) {
        return GraphicsAPI::D3D11;
    }
    
    // Check for D3D12 module
    if (GetModuleHandle(L"d3d12.dll")) {
        return GraphicsAPI::D3D12;
    }
    
    // Check for Vulkan module
    if (GetModuleHandle(L"vulkan-1.dll")) {
        return GraphicsAPI::VULKAN;
    }
    
    return GraphicsAPI::UNKNOWN;
}
