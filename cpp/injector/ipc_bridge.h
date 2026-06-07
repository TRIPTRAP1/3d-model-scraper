#pragma once

#include <string>
#include <vector>
#include <cstdint>

struct IPCMessage {
    uint32_t type;
    std::vector<uint8_t> data;
};

class IPCBridge {
public:
    IPCBridge(uint32_t pid);
    ~IPCBridge();
    
    /**
     * @brief Establish IPC connection to injected process
     */
    bool Connect();
    
    /**
     * @brief Send command to hooked process
     */
    bool SendMessage(const IPCMessage& msg);
    
    /**
     * @brief Receive response from hooked process
     */
    bool ReceiveMessage(IPCMessage& msg);
    
private:
    uint32_t pid_;
    void* pipe_handle_ = nullptr;
};
