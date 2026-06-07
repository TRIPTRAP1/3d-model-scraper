#pragma once

#include <string>
#include <cstdint>

class ProcessInjector {
public:
    /**
     * @brief Find process by executable name
     */
    static uint32_t FindProcessByName(const std::string& process_name);
    
    /**
     * @brief Inject DLL into target process
     */
    static bool InjectDLL(uint32_t pid, const std::string& dll_path);
    
    /**
     * @brief Check if DLL is injected
     */
    static bool IsDLLInjected(uint32_t pid, const std::string& dll_name);
    
private:
    static std::string GetProcessName(uint32_t pid);
};
