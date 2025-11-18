#!/usr/bin/bash
#
# Brief : Run COLMAP to generate a sparse reconstruction
# Usage : ./runcolmap.sh /path/to/project
# Author: Lyndon Hill
# Date  : 2025.10.01
#
# Description:
#
# Run colmap
# - Extract and match features
# - Set camera model (TODO)
# - Perform sparse reconstruction
# - Export models  (TODO not text)
# - Make sure project.ini file is saved
#
# Assumes that COLMAP has been build with CUDA support.

PROJECT_DIR=$1

COLMAP_BIN=colmap
IMAGE_DIR=${PROJECT_DIR}/images
DATABASE=${PROJECT_DIR}/project.db
SPARSE_DIR=${PROJECT_DIR}/sparse

echo Extracting features...
${COLMAP_BIN} feature_extractor \
  --database_path ${DATABASE} \
  --image_path ${IMAGE_DIR}

echo Matching features...
${COLMAP_BIN} exhaustive_matcher \
  --database_path ${DATABASE}

echo Sparse reconstruction...
${COLMAP_BIN} mapper \
  --database_path ${DATABASE} \
  --image_path ${IMAGE_DIR} \
  --output_path ${SPARSE_DIR} \
  --Mapper.num_threads $(nproc --all)

echo Export models...
${COLMAP_BIN} model_converter \
  --input_path ${SPARSE_DIR}/0 \
  --output_path ${PROJECT_DIR}/sparse.ply \
  --output_type PLY

echo Done
