add_library(screen_capture STATIC
    d3d11_backbuffer_hook.cpp
    d3d11_backbuffer_hook.h
    depth_buffer_extractor.cpp
    depth_buffer_extractor.h
    camera_params.h
    hook_manager.cpp
    hook_manager.h
)

target_include_directories(screen_capture PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(screen_capture PUBLIC glm::glm d3d11 dxgi)
