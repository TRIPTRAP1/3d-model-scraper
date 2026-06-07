add_library(buffer_capture STATIC
    mesh_extractor.cpp
    mesh_extractor.h
    texture_extractor.cpp
    texture_extractor.h
)

target_include_directories(buffer_capture PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
