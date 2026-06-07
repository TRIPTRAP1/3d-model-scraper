cmake_minimum_required(VERSION 3.16)
project(ScreenToSTL)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(WIN32)
    set(PLATFORM "windows")
else()
    message(FATAL_ERROR "This project currently supports Windows only")
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Find required packages
find_package(glm REQUIRED)

# Core modules
add_subdirectory(screen_capture)
add_subdirectory(depth_reconstruction)
add_subdirectory(mesh_generation)
add_subdirectory(mesh_cleanup)
add_subdirectory(export_engine)

# Main executable
add_executable(screen-to-stl
    src/main.cpp
)

target_link_libraries(screen-to-stl
    screen_capture
    depth_reconstruction
    mesh_generation
    mesh_cleanup
    export_engine
    glm::glm
    d3d11
    dxgi
)
