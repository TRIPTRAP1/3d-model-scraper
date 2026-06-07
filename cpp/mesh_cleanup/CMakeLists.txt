add_library(mesh_cleanup STATIC
    mesh_cleaner.cpp
    mesh_cleaner.h
)

target_include_directories(mesh_cleanup PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(mesh_cleanup PUBLIC glm::glm)
