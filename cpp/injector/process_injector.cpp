#include "process_injector.h"
#include <windows.h>
#include <tlhelp32.h>
#include <filesystem>

uint32_t ProcessInjector::FindProcessByName(const std::string& process_name) {
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snapshot == INVALID_HANDLE_VALUE) {
        return 0;
    }
    
    PROCESSENTRY32 entry;
    entry.dwSize = sizeof(PROCESSENTRY32);
    
    if (Process32First(snapshot, &entry)) {
        do {
            std::string exe_name(entry.szExeFile);
            if (exe_name.find(process_name) != std::string::npos) {
                CloseHandle(snapshot);
                return entry.th32ProcessID;
            }
        } while (Process32Next(snapshot, &entry));
    }
    
    CloseHandle(snapshot);
    return 0;
}

bool ProcessInjector::InjectDLL(uint32_t pid, const std::string& dll_path) {
    // Validate DLL exists
    if (!std::filesystem::exists(dll_path)) {
        return false;
    }
    
    // TODO: Implement DLL injection using CreateRemoteThread + LoadLibraryA
    return true;
}

bool ProcessInjector::IsDLLInjected(uint32_t pid, const std::string& dll_name) {
    HANDLE process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
    if (!process) {
        return false;
    }
    
    // TODO: Check if DLL is loaded in target process
    
    CloseHandle(process);
    return false;
}

std::string ProcessInjector::GetProcessName(uint32_t pid) {
    HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (!process) {
        return "";
    }
    
    char name[MAX_PATH];
    DWORD size = MAX_PATH;
    if (QueryFullProcessImageNameA(process, 0, name, &size)) {
        CloseHandle(process);
        return std::string(name);
    }
    
    CloseHandle(process);
    return "";
}
