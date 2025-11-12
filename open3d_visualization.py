import open3d as o3d
import numpy as np

def fix_obj_loading(file_path):
    print("⚠ Trying manual OBJ parsing...")
    return manual_obj_parsing(file_path)

def manual_obj_parsing(file_path):
    vertices = []
    faces = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('v ') and not line.startswith('vt ') and not line.startswith('vn '):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                # Face definition
                parts = line.split()
                if len(parts) >= 4:
                    face_vertices = []
                    for part in parts[1:4]:
                        vertex_index = part.split('/')[0]
                        if vertex_index.isdigit():
                            face_vertices.append(int(vertex_index) - 1)  # OBJ is 1-indexed

                    if len(face_vertices) == 3:
                        faces.append(face_vertices)

    if vertices and faces:
        print(f"✓ Manual parsing found: {len(vertices)} vertices, {len(faces)} faces")
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(np.array(vertices))
        mesh.triangles = o3d.utility.Vector3iVector(np.array(faces))
        mesh.compute_vertex_normals()
        return mesh


# Main execution
print("=== 3D Processing Pipeline with Open3D ===\n")

print("1. LOADING AND VISUALIZATION")
print("-" * 40)

file_path = "cat_3d.obj"
mesh = fix_obj_loading(file_path)

print(f"Final mesh loaded:")
print(f"Number of vertices: {len(mesh.vertices)}")
print(f"Number of triangles: {len(mesh.triangles)}")
print(f"Has vertex colors: {mesh.has_vertex_colors()}")
print(f"Has vertex normals: {mesh.has_vertex_normals()}")
print("Displaying original model...")
o3d.visualization.draw_geometries([mesh], window_name="Step 1: Loaded Model", width=800, height=600)

input("\nPress Enter to continue to Step 2...")

# Step 2: Conversion to Point Cloud
print("\n2. CONVERSION TO POINT CLOUD")
print("-" * 40)

# Convert mesh to point cloud
try:
    point_cloud = mesh.sample_points_poisson_disk(number_of_points=5000)
    print("✓ Point cloud created using Poisson disk sampling")
except:
    print("⚠ Poisson disk sampling failed, using uniform sampling")
    point_cloud = mesh.sample_points_uniformly(number_of_points=5000)
    print("✓ Point cloud created using uniform sampling")

print("Displaying point cloud...")
o3d.visualization.draw_geometries([point_cloud], window_name="Step 2: Point Cloud", width=800, height=600)

print(f"Number of points: {len(point_cloud.points)}")
print(f"Has colors: {point_cloud.has_colors()}")

input("\nPress Enter to continue to Step 3...")

# Step 3: Surface Reconstruction from Point Cloud
print("\n3. SURFACE RECONSTRUCTION FROM POINT CLOUD")
print("-" * 40)

# Poisson surface reconstruction
print("Performing Poisson surface reconstruction...")
try:
    mesh_reconstructed, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        point_cloud, depth=8
    )
    print("✓ Surface reconstruction completed")

    # Remove artifacts
    bbox = point_cloud.get_axis_aligned_bounding_box()
    mesh_reconstructed = mesh_reconstructed.crop(bbox)
    print("✓ Artifacts removed using bounding box crop")

except Exception as e:
    print(f"⚠ Poisson reconstruction failed: {e}")
    print("Using ball pivoting as fallback...")
    distances = point_cloud.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 3 * avg_dist
    mesh_reconstructed = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        point_cloud, o3d.utility.DoubleVector([radius, radius * 2]))
    print("✓ Surface reconstruction completed using ball pivoting")

print("Displaying reconstructed mesh...")
o3d.visualization.draw_geometries([mesh_reconstructed], window_name="Step 3: Reconstructed Mesh", width=800, height=600)

print(f"Number of vertices: {len(mesh_reconstructed.vertices)}")
print(f"Number of triangles: {len(mesh_reconstructed.triangles)}")
print(f"Has vertex colors: {mesh_reconstructed.has_vertex_colors()}")

input("\nPress Enter to continue to Step 4...")

# Step 4: Voxelization
print("\n4. VOXELIZATION")
print("-" * 40)

# Convert point cloud to voxel grid
voxel_size = 0.05
voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size)
print(f"✓ Voxel grid created with voxel size: {voxel_size}")

print("Displaying voxel grid...")
o3d.visualization.draw_geometries([voxel_grid], window_name="Step 4: Voxel Grid", width=800, height=600)

voxels = voxel_grid.get_voxels()
print(f"Number of voxels: {len(voxels)}")
print(f"Has colors: {voxel_grid.has_colors()}")

input("\nPress Enter to continue to Step 5...")

# Step 5: Plane
print("\n5. ADDING A PLANE")
print("-" * 40)

# Get cat bounds
bbox = mesh_reconstructed.get_axis_aligned_bounding_box()
bbox_center = bbox.get_center()
bbox_extent = bbox.get_extent()

plane_width = bbox_extent[1] * 2.0  # Height of plane
plane_depth = 0.05  # Thin plane
plane_height = bbox_extent[2] * 2.0  # Width of plane

# Create vertical plane (rotated)
plane = o3d.geometry.TriangleMesh.create_box(width=plane_depth, height=plane_width, depth=plane_height)
plane.paint_uniform_color([0.8, 0.3, 0.3])
plane.rotate(plane.get_rotation_matrix_from_xyz([0, 0, np.pi/2]))

# Position to cut through the center of the cat
plane_center = plane.get_center()
translation = [
    bbox_center[0] - plane_center[0],
    bbox_center[1] - plane_center[1],
    bbox_center[2] - plane_center[2]
]
plane.translate(translation)

print("✓ Vertical plane created - cutting through cat")
print("Displaying object with the plane...")
o3d.visualization.draw_geometries([mesh_reconstructed, plane],
                                 window_name="Step 5: Plane Cutting Through Cat",
                                 width=800, height=600)

mesh_center = bbox_center

input("\nPress Enter to continue to Step 6...")

# Step 6: Surface Clipping
print("\n6. SURFACE CLIPPING")
print("-" * 40)

# Create a clipping plane
clipping_plane = [1, 0, 0, -mesh_center[0] + 0.3]  # Plane equation: x - (center_x - 0.3) = 0

# Convert mesh to point cloud
points = np.asarray(mesh_reconstructed.vertices)
triangles = np.asarray(mesh_reconstructed.triangles)

if len(points) > 0 and len(triangles) > 0:
    # Find points on the left side of the plane (keep points where ax + by + cz + d < 0)
    a, b, c, d = clipping_plane
    distances = a * points[:, 0] + b * points[:, 1] + c * points[:, 2] + d
    keep_indices = np.where(distances < 0)[0]

    vertex_mask = np.zeros(len(points), dtype=bool)
    vertex_mask[keep_indices] = True

    new_vertices = points[keep_indices]
    index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(keep_indices)}

    new_triangles = []
    for triangle in triangles:
        if (triangle[0] in keep_indices and
                triangle[1] in keep_indices and
                triangle[2] in keep_indices):
            new_triangles.append([index_map[triangle[0]], index_map[triangle[1]], index_map[triangle[2]]])

    clipped_mesh = o3d.geometry.TriangleMesh()
    clipped_mesh.vertices = o3d.utility.Vector3dVector(new_vertices)
    clipped_mesh.triangles = o3d.utility.Vector3iVector(new_triangles)
    clipped_mesh.compute_vertex_normals()

    print("✓ Surface clipping completed (removed right side of the object)")
else:
    print("⚠ Cannot perform clipping - no valid geometry")
    clipped_mesh = mesh_reconstructed

print("Displaying clipped mesh...")
o3d.visualization.draw_geometries([clipped_mesh], window_name="Step 6: Clipped Mesh", width=800, height=600)

print(f"Number of remaining vertices: {len(clipped_mesh.vertices)}")
print(f"Number of remaining triangles: {len(clipped_mesh.triangles)}")
print(f"Has vertex colors: {clipped_mesh.has_vertex_colors()}")
print(f"Has vertex normals: {clipped_mesh.has_vertex_normals()}")

input("\nPress Enter to continue to Step 7...")

# Step 7: Working with Color and Extremes
print("\n7. WORKING WITH COLOR AND EXTREMES")
print("-" * 40)

# Remove original colors and apply gradient along Z-axis
vertices = np.asarray(clipped_mesh.vertices)

if len(vertices) > 0:
    z_coords = vertices[:, 2]
    z_min, z_max = np.min(z_coords), np.max(z_coords)

    # Create color gradient from blue to red based on Z-coordinate
    colors = np.zeros((len(vertices), 3))
    for i, z in enumerate(z_coords):
        # Normalize z coordinate to [0, 1]
        t = (z - z_min) / (z_max - z_min) if z_max != z_min else 0.5
        # Blue (0,0,1) to Red (1,0,0) gradient
        colors[i] = [t, 0.3, 1 - t]

    clipped_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
    print("✓ Original colors removed and Z-axis gradient applied")

    # Find extreme points along Z-axis
    min_point = vertices[np.argmin(z_coords)]
    max_point = vertices[np.argmax(z_coords)]

    print(f"Minimum point (lowest Z): ({min_point[0]:.3f}, {min_point[1]:.3f}, {min_point[2]:.3f})")
    print(f"Maximum point (highest Z): ({max_point[0]:.3f}, {max_point[1]:.3f}, {max_point[2]:.3f})")

    # Create spheres to highlight extreme points
    min_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
    min_sphere.paint_uniform_color([0, 1, 0])  # Green for minimum
    min_sphere.translate(min_point)

    max_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
    max_sphere.paint_uniform_color([1, 0, 0])  # Red for maximum
    max_sphere.translate(max_point)

    print("✓ Extreme points highlighted with spheres")
    print("Displaying colored mesh with extreme points...")
    o3d.visualization.draw_geometries([clipped_mesh, min_sphere, max_sphere],
                                      window_name="Step 7: Gradient Colors & Extreme Points",
                                      width=800, height=600)
else:
    print("⚠ Cannot process colors and extremes - no vertices available")

print("\n=== PROCESSING COMPLETE ===")
print("All 7 steps have been successfully executed!")
print(f"Final model has {len(clipped_mesh.vertices)} vertices and {len(clipped_mesh.triangles)} triangles")