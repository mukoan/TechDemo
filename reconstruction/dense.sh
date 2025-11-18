#!/usr/bin/bash
#
# Brief : Run dense reconstruction using COLMAP
# Usage : ./dense.sh /path/to/project
# Author: Lyndon Hill
# Date  : 2025.10.01
#
# Description:
#
# Run dense reconstruction using sparse COLMAP reconstruction

PROJECT_DIR=$1

COLMAP_BIN=colmap
IMAGE_DIR=${PROJECT_DIR}/images
DATABASE=${PROJECT_DIR}/project.db
SPARSE_DIR=${PROJECT_DIR}/sparse
DENSE_DIR=${PROJECT_DIR}/dense

mkdir ${DENSE_DIR}

echo Undistort images...
${COLMAP_BIN} image_undistorter \
    --image_path ${IMAGE_DIR} \
    --input_path ${SPARSE_DIR}/0 \
    --output_path ${DENSE_DIR} \
    --output_type COLMAP \
    --max_image_size 2000

echo Patchmatch...
${COLMAP_BIN} patch_match_stereo \
    --workspace_path ${DENSE_DIR} \
    --workspace_format COLMAP \
    --PatchMatchStereo.geom_consistency true

echo Stereo fusion...
${COLMAP_BIN} stereo_fusion \
    --workspace_path ${DENSE_DIR} \
    --workspace_format COLMAP \
    --input_type geometric \
    --output_path ${DENSE_DIR}/fused.ply

echo Poisson meshing...
${COLMAP_BIN} poisson_mesher \
    --input_path ${DENSE_DIR}/fused.ply \
    --output_path ${DENSE_DIR}/meshed-poisson.ply

echo Delaunay meshing...
${COLMAP_BIN} delaunay_mesher \
    --input_path ${DENSE_DIR} \
    --output_path ${DENSE_DIR}/meshed-delaunay.ply

echo Done
