add_library(graphics_hooks STATIC
    d3d11_hook.cpp
    d3d11_hook.h
    d3d12_hook.cpp
    d3d12_hook.h
    vulkan_hook.cpp
    vulkan_hook.h
    hook_manager.cpp
    hook_manager.h
)

target_include_directories(graphics_hooks PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(graphics_hooks PUBLIC d3d11 d3d12 vulkan)
