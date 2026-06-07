add_library(mesh_generation STATIC
    marching_cubes.cpp
    marching_cubes.h
    mesh_data.h
)

target_include_directories(mesh_generation PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(mesh_generation PUBLIC glm::glm)
