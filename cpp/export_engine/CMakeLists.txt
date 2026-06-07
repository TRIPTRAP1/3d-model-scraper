add_library(export_engine STATIC
    obj_exporter.cpp
    obj_exporter.h
    glb_exporter.cpp
    glb_exporter.h
    stl_exporter.cpp
    stl_exporter.h
)

target_include_directories(export_engine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(export_engine PUBLIC ZLIB::ZLIB glm::glm)
