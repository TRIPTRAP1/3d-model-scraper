#include <iostream>
#include <memory>
#include <vector>
#include <cstring>
#include "../screen_capture/hook_manager.h"
#include "../depth_reconstruction/point_cloud_generator.h"
#include "../mesh_generation/marching_cubes.h"
#include "../mesh_cleanup/mesh_cleaner.h"
#include "../export_engine/stl_exporter.h"

void PrintUsage(const char* program_name) {
    std::cout << "Usage: " << program_name << " [options]\n\n";
    std::cout << "Options:\n";
    std::cout << "  --help              Show this help message\n";
    std::cout << "  --width <pixels>    Set capture width (default: 1920)\n";
    std::cout << "  --height <pixels>   Set capture height (default: 1080)\n";
    std::cout << "  --voxel <size>      Voxel size in world units (default: 0.02)\n";
    std::cout << "  --output <path>     Output STL file path (default: model.stl)\n";
}

int main(int argc, char* argv[]) {
    std::cout << "\n=== Screen to STL Converter ===\n";
    std::cout << "Phase 1: Screen Capture & Depth Extraction\n\n";
    
    // Parse command line arguments
    std::string output_path = "model.stl";
    uint32_t capture_width = 1920;
    uint32_t capture_height = 1080;
    float voxel_size = 0.02f;
    
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--help") {
            PrintUsage(argv[0]);
            return 0;
        } else if (arg == "--output" && i + 1 < argc) {
            output_path = argv[++i];
        } else if (arg == "--width" && i + 1 < argc) {
            capture_width = std::stoul(argv[++i]);
        } else if (arg == "--height" && i + 1 < argc) {
            capture_height = std::stoul(argv[++i]);
        } else if (arg == "--voxel" && i + 1 < argc) {
            voxel_size = std::stof(argv[++i]);
        }
    }
    
    // Initialize screen capture
    std::cout << "[1/5] Initializing screen capture...\n";
    auto capture_manager = std::make_unique<ScreenCaptureManager>();
    if (!capture_manager->Initialize()) {
        std::cerr << "ERROR: Failed to initialize screen capture\n";
        return 1;
    }
    std::cout << "  ✓ Screen capture ready\n";
    
    if (!capture_manager->IsReady()) {
        std::cerr << "ERROR: Capture system not ready\n";
        return 1;
    }
    
    // Allocate buffers
    std::cout << "\n[2/5] Allocating capture buffers...\n";
    size_t pixel_count = capture_width * capture_height;
    auto rgba_buffer = std::make_unique<uint8_t[]>(pixel_count * 4);
    auto depth_buffer = std::make_unique<float[]>(pixel_count);
    std::cout << "  ✓ Allocated " << (pixel_count * 8 / 1024.0f / 1024.0f) << " MB\n";
    
    // Capture current frame
    std::cout << "\n[3/5] Capturing frame and depth buffer...\n";
    uint32_t actual_width, actual_height;
    if (!capture_manager->CaptureFrame(rgba_buffer.get(), depth_buffer.get(),
                                       actual_width, actual_height)) {
        std::cerr << "ERROR: Failed to capture frame\n";
        return 1;
    }
    std::cout << "  ✓ Captured " << actual_width << "x" << actual_height << " frame\n";
    std::cout << "  ✓ Extracted depth buffer\n";
    
    // Reconstruct 3D point cloud
    std::cout << "\n[4/5] Reconstructing 3D point cloud...\n";
    std::vector<glm::vec3> point_cloud;
    std::vector<glm::vec3> point_colors;
    const CameraParams& camera = capture_manager->GetCameraParams();
    
    size_t point_count = PointCloudGenerator::GeneratePointCloud(
        rgba_buffer.get(),
        depth_buffer.get(),
        actual_width,
        actual_height,
        camera,
        point_cloud,
        &point_colors
    );
    
    std::cout << "  ✓ Generated " << point_count << " 3D points\n";
    
    // Generate mesh from point cloud
    std::cout << "\n[5/5] Generating watertight mesh...\n";
    Mesh output_mesh;
    if (!MarchingCubes::GenerateMesh(point_cloud, voxel_size, output_mesh)) {
        std::cerr << "ERROR: Failed to generate mesh\n";
        return 1;
    }
    std::cout << "  ✓ Generated " << output_mesh.GetVertexCount() << " vertices\n";
    std::cout << "  ✓ Generated " << output_mesh.GetTriangleCount() << " triangles\n";
    
    // Cleanup mesh
    std::cout << "\n[6/5] Optimizing mesh for printing...\n";
    MeshCleaner::OptimizeForPrinting(output_mesh);
    std::cout << "  ✓ Optimized mesh\n";
    std::cout << "  ✓ Final: " << output_mesh.GetTriangleCount() << " triangles\n";
    
    // Export to STL
    std::cout << "\n[7/5] Exporting STL...\n";
    if (!STLExporter::ExportBinary(output_mesh, output_path)) {
        std::cerr << "ERROR: Failed to export STL\n";
        return 1;
    }
    std::cout << "  ✓ Exported: " << output_path << "\n";
    
    // Get mesh bounds
    glm::vec3 min_bound, max_bound;
    output_mesh.GetBounds(min_bound, max_bound);
    glm::vec3 size = max_bound - min_bound;
    
    std::cout << "\n=== SUCCESS ===\n";
    std::cout << "Model bounds:\n";
    std::cout << "  X: " << size.x << " units\n";
    std::cout << "  Y: " << size.y << " units\n";
    std::cout << "  Z: " << size.z << " units\n";
    std::cout << "\nReady for 3D printing!\n\n";
    
    return 0;
}
