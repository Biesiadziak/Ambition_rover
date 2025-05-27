import open3d as o3d
pcd = o3d.io.read_point_cloud("marsyard_cloud.ply")
o3d.io.write_point_cloud("marsayrd_cloud.pcd", pcd)
