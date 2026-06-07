#include "../graphics_hooks/hook_manager.h"
#include <iostream>
#include <thread>

int main() {
    std::cout << "Graphics Capture Engine - Starting\n";
    
    HookManager manager;
    
    // Detect and initialize graphics API
    auto api = manager.Initialize();
    
    switch (api) {
        case HookManager::GraphicsAPI::D3D11:
            std::cout << "Hooked: Direct3D 11\n";
            break;
        case HookManager::GraphicsAPI::D3D12:
            std::cout << "Hooked: Direct3D 12\n";
            break;
        case HookManager::GraphicsAPI::VULKAN:
            std::cout << "Hooked: Vulkan\n";
            break;
        default:
            std::cout << "Failed to detect graphics API\n";
            return 1;
    }
    
    manager.SetCaptureEnabled(true);
    
    // Keep running
    std::cout << "\nCapture engine running. Press Ctrl+C to exit.\n";
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    manager.Shutdown();
    return 0;
}
