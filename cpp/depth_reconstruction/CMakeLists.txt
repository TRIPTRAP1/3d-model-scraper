add_library(depth_reconstruction STATIC
    point_cloud_generator.cpp
    point_cloud_generator.h
)

target_include_directories(depth_reconstruction PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(depth_reconstruction PUBLIC glm::glm)
