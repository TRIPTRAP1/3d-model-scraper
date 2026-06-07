cmake_minimum_required(VERSION 3.16)
project(GraphicsCapture)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Platform detection
if(WIN32)
    set(PLATFORM "windows")
else()
    message(FATAL_ERROR "This project currently supports Windows only")
endif()

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Third-party libraries
find_package(glm REQUIRED)
find_package(ZLIB REQUIRED)

# Core modules
add_subdirectory(graphics_hooks)
add_subdirectory(buffer_capture)
add_subdirectory(mesh_processor)
add_subdirectory(export_engine)
add_subdirectory(injector)

# Main executable
add_executable(graphics-capture-daemon
    src/main.cpp
)

target_link_libraries(graphics-capture-daemon
    graphics_hooks
    buffer_capture
    mesh_processor
    export_engine
    injector
    glm::glm
    ZLIB::ZLIB
)
