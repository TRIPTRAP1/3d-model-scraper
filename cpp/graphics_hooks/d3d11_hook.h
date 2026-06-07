#pragma once

#include <d3d11.h>
#include <vector>
#include <memory>
#include <functional>

class CapturedMesh;

/**
 * @brief Direct3D 11 graphics interception hook
 * 
 * Intercepts D3D11 draw calls and captures vertex/index buffers,
 * constant buffers, and render target textures.
 */
class D3D11Hook {
public:
    D3D11Hook();
    ~D3D11Hook();

    /**
     * @brief Initialize D3D11 hooking
     * @return true if successful
     */
    bool Initialize();

    /**
     * @brief Shutdown D3D11 hooking
     */
    void Shutdown();

    /**
     * @brief Is hooking currently active?
     */
    bool IsHooked() const { return hooked_; }

    /**
     * @brief Capture next draw call's geometry
     */
    void CaptureNextDraw();

    /**
     * @brief Get captured meshes
     */
    const std::vector<CapturedMesh>& GetCapturedMeshes() const { return captured_meshes_; }

    /**
     * @brief Clear captured meshes
     */
    void ClearCapturedMeshes() { captured_meshes_.clear(); }

private:
    bool hooked_ = false;

    // Original D3D11 function pointers
    using DrawIndexedFunc = void(__stdcall*)(ID3D11DeviceContext*, UINT, UINT, INT);
    using DrawFunc = void(__stdcall*)(ID3D11DeviceContext*, UINT, UINT);
    using CreateBufferFunc = HRESULT(__stdcall*)(ID3D11Device*, const D3D11_BUFFER_DESC*, const D3D11_SUBRESOURCE_DATA*, ID3D11Buffer**);

    DrawIndexedFunc original_draw_indexed_ = nullptr;
    DrawFunc original_draw_ = nullptr;
    CreateBufferFunc original_create_buffer_ = nullptr;

    std::vector<CapturedMesh> captured_meshes_;
    bool capture_next_draw_ = false;

    // Hook implementations (static for compatibility)
    static void __stdcall HookDrawIndexed(ID3D11DeviceContext* context, UINT index_count, UINT start_index, INT base_vertex);
    static void __stdcall HookDraw(ID3D11DeviceContext* context, UINT vertex_count, UINT start_vertex);
    static HRESULT __stdcall HookCreateBuffer(ID3D11Device* device, const D3D11_BUFFER_DESC* desc, const D3D11_SUBRESOURCE_DATA* initial_data, ID3D11Buffer** buffer);

    // Helper to extract buffer data from GPU
    void ExtractBufferData(ID3D11DeviceContext* context, ID3D11Buffer* buffer, void** out_data, size_t* out_size);
};
