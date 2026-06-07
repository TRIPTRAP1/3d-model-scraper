add_library(injector STATIC
    process_injector.cpp
    process_injector.h
    ipc_bridge.cpp
    ipc_bridge.h
)

target_include_directories(injector PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
