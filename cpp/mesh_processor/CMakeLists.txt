add_library(mesh_processor STATIC
    mesh_optimizer.cpp
    mesh_optimizer.h
)

target_include_directories(mesh_processor PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(mesh_processor PUBLIC glm::glm)
