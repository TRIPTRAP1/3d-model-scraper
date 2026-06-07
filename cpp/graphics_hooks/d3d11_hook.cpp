#include "d3d11_hook.h"
#include <cstring>
#include <stdexcept>

// Global instance for hook callbacks (not ideal, but necessary for C++ interop with C APIs)
static D3D11Hook* g_d3d11_hook_instance = nullptr;

D3D11Hook::D3D11Hook() {
    g_d3d11_hook_instance = this;
}

D3D11Hook::~D3D11Hook() {
    if (hooked_) {
        Shutdown();
    }
    g_d3d11_hook_instance = nullptr;
}

bool D3D11Hook::Initialize() {
    // TODO: Implement actual hooking
    // 1. Find D3D11Device and D3D11DeviceContext in memory
    // 2. Hook vftable entries
    // 3. Save original function pointers
    
    hooked_ = true;
    return true;
}

void D3D11Hook::Shutdown() {
    if (hooked_) {
        // TODO: Unhook vftable entries
        // TODO: Restore original functions
        hooked_ = false;
    }
}

void D3D11Hook::CaptureNextDraw() {
    capture_next_draw_ = true;
}

void D3D11Hook::ExtractBufferData(ID3D11DeviceContext* context, ID3D11Buffer* buffer, void** out_data, size_t* out_size) {
    if (!buffer || !context) return;

    // Create staging buffer for readback
    D3D11_BUFFER_DESC desc;
    buffer->GetDesc(&desc);

    D3D11_BUFFER_DESC staging_desc = desc;
    staging_desc.Usage = D3D11_USAGE_STAGING;
    staging_desc.BindFlags = 0;
    staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;

    ID3D11Device* device = nullptr;
    context->GetDevice(&device);
    if (!device) return;

    ID3D11Buffer* staging_buffer = nullptr;
    HRESULT hr = device->CreateBuffer(&staging_desc, nullptr, &staging_buffer);
    if (FAILED(hr)) {
        device->Release();
        return;
    }

    // Copy buffer to staging
    context->CopyResource(staging_buffer, buffer);

    // Map and read
    D3D11_MAPPED_SUBRESOURCE mapped;
    hr = context->Map(staging_buffer, 0, D3D11_MAP_READ, 0, &mapped);
    if (SUCCEEDED(hr)) {
        *out_size = desc.ByteWidth;
        *out_data = malloc(*out_size);
        memcpy(*out_data, mapped.pData, *out_size);
        context->Unmap(staging_buffer, 0);
    }

    staging_buffer->Release();
    device->Release();
}

void __stdcall D3D11Hook::HookDrawIndexed(ID3D11DeviceContext* context, UINT index_count, UINT start_index, INT base_vertex) {
    if (g_d3d11_hook_instance && g_d3d11_hook_instance->capture_next_draw_) {
        // TODO: Extract vertex/index buffers and textures
        g_d3d11_hook_instance->capture_next_draw_ = false;
    }

    // Call original function
    if (g_d3d11_hook_instance && g_d3d11_hook_instance->original_draw_indexed_) {
        g_d3d11_hook_instance->original_draw_indexed_(context, index_count, start_index, base_vertex);
    }
}

void __stdcall D3D11Hook::HookDraw(ID3D11DeviceContext* context, UINT vertex_count, UINT start_vertex) {
    if (g_d3d11_hook_instance && g_d3d11_hook_instance->original_draw_) {
        g_d3d11_hook_instance->original_draw_(context, vertex_count, start_vertex);
    }
}

HRESULT __stdcall D3D11Hook::HookCreateBuffer(ID3D11Device* device, const D3D11_BUFFER_DESC* desc, const D3D11_SUBRESOURCE_DATA* initial_data, ID3D11Buffer** buffer) {
    if (g_d3d11_hook_instance && g_d3d11_hook_instance->original_create_buffer_) {
        return g_d3d11_hook_instance->original_create_buffer_(device, desc, initial_data, buffer);
    }
    return E_FAIL;
}
