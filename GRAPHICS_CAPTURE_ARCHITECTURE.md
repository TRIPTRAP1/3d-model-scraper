# Graphics Capture Architecture - Ninja Ripper Style

**Status**: Full production-grade graphics interception framework

## Overview

This is a **graphics API interception system** that:
- 🔌 **Hooks graphics APIs** (Direct3D 11/12, Vulkan, OpenGL)
- 📸 **Intercepts vertex/index buffers** before rendering
- 🎯 **Captures meshes with textures & materials** at render time
- ⚙️ **Preserves rigging & animations** (GPU skinning)
- 📤 **Exports to multiple formats** (OBJ, GLB, STL)

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│  Python CLI/TUI Interface (User-facing)         │
│  └─ Session management, configuration, export   │
├─────────────────────────────────────────────────┤
│  IPC Bridge (Named Pipes / Memory Mapped)       │
│  └─ Command routing, data transfer              │
├─────────────────────────────────────────────────┤
│  C++ Injector (DLL Injection Agent)             │
│  └─ Process attachment, hook initialization     │
├─────────────────────────────────────────────────┤
│  Graphics Capture Engine (Core Logic)           │
│  ├─ D3D11/D3D12 Hook Layer                      │
│  ├─ Vulkan Hook Layer                           │
│  ├─ OpenGL Hook Layer (optional)                │
│  └─ Vertex Buffer Interception                  │
├─────────────────────────────────────────────────┤
│  Mesh Processor (Post-capture)                  │
│  ├─ Vertex/Index buffer parsing                 │
│  ├─ Texture extraction                          │
│  ├─ Material reconstruction                     │
│  └─ Format conversion                           │
├─────────────────────────────────────────────────┤
│  Export Engine                                  │
│  ├─ OBJ/MTL export                              │
│  ├─ GLB/GLTF export                             │
│  ├─ FBX export (with rigging)                   │
│  └─ STL export                                  │
└─────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. **Injector (`cpp/injector/`)**
- Process discovery & attachment
- DLL injection mechanism
- Hook initialization
- IPC setup

### 2. **Graphics Hooks (`cpp/graphics_hooks/`)**

#### D3D11 Hook
- Hook `ID3D11Device::CreateBuffer`
- Hook `ID3D11DeviceContext::DrawIndexed` / `Draw`
- Intercept vertex/index buffers
- Capture constant buffers (transforms)
- Extract textures from render targets

#### D3D12 Hook
- Hook command list recording
- Intercept descriptor heaps
- Capture GPU buffers
- Handle resource barriers

#### Vulkan Hook
- Hook `vkCreateBuffer` / `vkBindBufferMemory`
- Hook `vkCmdDrawIndexed` / `vkCmdDraw`
- Intercept descriptor sets
- Handle memory mapping

### 3. **Buffer Capture (`cpp/buffer_capture/`)**
```cpp
struct CapturedMesh {
    std::vector<Vertex> vertices;      // Position, Normal, UV, Color
    std::vector<uint32_t> indices;     // Triangle indices
    std::vector<Texture> textures;     // Diffuse, Normal, Specular, etc.
    std::vector<Material> materials;   // PBR material data
    Transform worldMatrix;             // Object position/rotation/scale
    std::string name;                  // Mesh identifier
    uint64_t timestamp;                // Capture time
};
```

### 4. **Mesh Processing (`cpp/mesh_processor/`)**
- Vertex deduplication
- Normal recalculation
- Tangent/binormal generation
- UV unwrapping (optional)
- Mesh optimization

### 5. **Export Engine (`cpp/export_engine/`)**
- Multi-format support
- Material baking
- Rigging/skeleton export
- Animation sampling

## Key Technical Challenges & Solutions

### Challenge 1: **Buffer Readback from GPU**
**Problem**: Captured buffers are on GPU VRAM, not CPU-accessible

**Solution**:
```cpp
// D3D11: Create staging buffer
D3D11_BUFFER_DESC desc = originalBuffer->GetDesc();
desc.Usage = D3D11_USAGE_STAGING;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
ID3D11Buffer* stagingBuffer;
device->CreateBuffer(&desc, nullptr, &stagingBuffer);
deviceContext->CopyResource(stagingBuffer, originalBuffer);
// Now read from stagingBuffer
```

### Challenge 2: **Constant Buffer Extraction**
**Problem**: Transforms (World, View, Projection) are in shader constants

**Solution**:
- Hook `UpdateSubresource` / `Map` calls
- Extract constant buffer data
- Parse shader bytecode to identify matrix layouts
- Reconstruct model/world transforms

### Challenge 3: **Texture Binding**
**Problem**: Textures are bound through descriptor heaps/tables

**Solution**:
- Track texture bindings at draw time
- Snapshot render targets before clear
- Readback textures to CPU
- Auto-detect texture type (diffuse, normal, specular, etc.)

### Challenge 4: **Multi-frame Scenes**
**Problem**: Complex scenes need multiple draw calls to capture

**Solution**:
- Session-based capture (capture multiple frames)
- Auto-merge duplicate meshes
- Scene graph reconstruction
- Deduplication by geometry hash

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Process injection framework
- [ ] Basic D3D11 hooking
- [ ] Simple mesh capture (vertex + index)
- [ ] OBJ export

### Phase 2: Enhancement (Weeks 3-4)
- [ ] Texture capture & export
- [ ] Material reconstruction
- [ ] Normal/tangent calculation
- [ ] D3D12 support

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] Vulkan support
- [ ] Rigging extraction (GPU skinning)
- [ ] Animation keyframe sampling
- [ ] FBX/GLB export with rigging

### Phase 4: Polish (Week 7)
- [ ] Python CLI wrapper
- [ ] TUI interface
- [ ] Error handling & edge cases
- [ ] Performance optimization

## Dependencies

**C++ Libraries**:
- `Windows.h` (Windows APIs)
- `d3d11.h`, `d3d12.h` (Direct3D)
- `vulkan.h` (Vulkan)
- `zlib` (compression)
- `glm` (mathematics)

**Python**:
- `ctypes` (C interop)
- `rich` (TUI)
- `numpy` (data processing)
- `pillow` (image handling)

## Safety & Ethics

✅ **Legitimate Uses**:
- Game modding (with developer permission)
- Asset research for educational purposes
- Game analysis & reverse engineering (legal in many jurisdictions)
- VFX/Animation research

⚠️ **Disclaimer**:
- Ensure compliance with game ToS
- Respect intellectual property
- Use only on personally-owned software
- No commercial redistribution of captured assets

## Expected Output

When complete, users can:
```bash
# Launch application
python src/cli.py

# Select D3D11 WoW process
> Process: World of Warcraft (PID: 1234)

# Inject capture engine
> Injecting graphics hook...
> ✓ Hooked ID3D11DeviceContext::DrawIndexed
> ✓ Hooked ID3D11Device::CreateBuffer

# Capture meshes interactively
> Move camera to character
> Press [SPACEBAR] to capture frame
> ✓ Captured 47 meshes
> ✓ Extracted 12 textures

# Export
> Export format: [1] OBJ [2] GLB [3] FBX
> Selected: FBX (with rigging)
> ✓ Exported: character_capture.fbx (45 MB)
```

## Timeline

Estimated: **6-8 weeks** for production-ready implementation

This represents a **substantial engineering effort** equivalent to:
- Building a graphics debugger (like RenderDoc/PIX)
- Custom 3D pipeline integration
- Multiple graphics API backends
