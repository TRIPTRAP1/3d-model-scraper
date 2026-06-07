#include "texture_extractor.h"
#include <algorithm>

TextureData TextureExtractor::ExtractD3D11Texture() {
    TextureData texture;
    // TODO: Implement D3D11 texture extraction
    return texture;
}

TextureData TextureExtractor::ExtractVulkanTexture() {
    TextureData texture;
    // TODO: Implement Vulkan texture extraction
    return texture;
}

std::string TextureExtractor::DetectTextureType(const std::string& name) {
    std::string lower_name = name;
    std::transform(lower_name.begin(), lower_name.end(), lower_name.begin(), ::tolower);
    
    if (lower_name.find("normal") != std::string::npos) return "normal";
    if (lower_name.find("spec") != std::string::npos) return "specular";
    if (lower_name.find("rough") != std::string::npos) return "roughness";
    if (lower_name.find("metal") != std::string::npos) return "metallic";
    if (lower_name.find("ao") != std::string::npos || lower_name.find("ambient") != std::string::npos) return "ambient_occlusion";
    if (lower_name.find("emissive") != std::string::npos) return "emissive";
    
    return "diffuse";
}
