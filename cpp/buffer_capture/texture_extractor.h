#pragma once

#include <string>
#include <vector>
#include <cstdint>

struct TextureData {
    std::string name;
    std::vector<uint8_t> data;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t format = 0; // DXGI_FORMAT or VK_FORMAT
};

class TextureExtractor {
public:
    // Extract texture from D3D11 render target
    static TextureData ExtractD3D11Texture();
    
    // Extract texture from Vulkan image
    static TextureData ExtractVulkanTexture();
    
    // Detect texture type (diffuse, normal, specular, etc.)
    static std::string DetectTextureType(const std::string& name);
};
