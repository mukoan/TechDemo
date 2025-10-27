#!/usr/bin/env bash
#
# File  : runomvs.sh
# Brief : Script to run OpenMVS tools on a COLMAP project
# Author: Lyndon Hill
# Date  : 2025.10.01
#
# Description:
# This script assumes that the COLMAP project has been created and a
# sparse reconstruction has been performed.
# The script makes a dense reconstruction, generating refined and textured
# (colour) mesh.
   

# Check number of arguments
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <project_directory>"
  exit 1
fi

PROJECT_DIR=$1
cd ${PROJECT_DIR}/dense || { echo "Dense directory not found!"; exit 1; }

# Run OpenMVS tools

# 1. Convert COLMAP data to OpenMVS format
InterfaceCOLMAP -i . -o project.mvs

# 2. Make the point cloud dense
DensifyPointCloud project.mvs

# 3. Reconstruct the mesh from the dense point cloud
ReconstructMesh project_dense.mvs

# 4. Improve mesh quality
RefineMesh --resolution-level 1 project_dense.mvs -m project_dense_mesh.ply -o project_dense_mesh_refine.mvs

# 5. Texture the mesh (add colour)
TextureMesh project_dense_refine.mvs -m project_dense_mesh.ply -o project_dense_mesh_refine_texture.mvs

echo "OpenMVS processing done."
