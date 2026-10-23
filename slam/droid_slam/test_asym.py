"""
File:   test_asym.py
Brief:  Asymmetrical Stereo Camera source; rectified images input
Author: Based on test_euroc.py, demo.py and view_reconstruction.py
        Edited by Lyndon Hill
Date:   2026.10.13
"""

import sys
sys.path.append('droid_slam')

from tqdm import tqdm
import numpy as np
import torch
import cv2
import os
import glob
import argparse

from pathlib import Path
from droid import Droid
from droid_async import DroidAsync

import droid_backends
import open3d as o3d
from lietorch import SE3
from cuda_timer import CudaTimer

import load_settings


def read_timestamps(ts_path: str):
    """
    Read timestamps file

    Params
      ts_path: path to timestamps.txt file

    Return
      timestamps
    """
    timestamps = []
    with open(ts_path, "r") as f:
        line = f.readline()
        while line:
            filename, ts = line.strip().split(" ")
            timestamps.append(float(ts))
            line = f.readline()

    return timestamps


def show_image(image):
    image = image.permute(1, 2, 0).cpu().numpy()
    cv2.imshow('image', image / 255.0)
    cv2.waitKey(1)


def image_stream(datapath, image_size=[320, 512], stereo=False, stride=1):
    """
    image generator
    """

    ht0, wd0 = [480, 752]

    # Load intrinsics
    settings_file = os.path.join(datapath, "settings.yaml")
    fx, fy, cx, cy, src_width, src_height = load_settings.read_file(settings_file)

    # Scale intrinsics to wd0 x ht0
    sx = wd0/src_width
    sy = ht0/src_height
    intrinsics_vec = [sx*fx, sy*fy, sx*cx, sy*cy]

    # read all png images in folder
    images_left = sorted(glob.glob(os.path.join(datapath, 'left/*.png')))[::stride]
    images_right = [x.replace('left', 'right') for x in images_left]

    data_list = []
    for t, (imgL, imgR) in enumerate(zip(images_left, images_right)):
        if stereo and not os.path.isfile(imgR):
            continue

        img_l = cv2.resize(cv2.imread(imgL), (wd0, ht0))
        if stereo:
            img_r = cv2.resize(cv2.imread(imgR), (wd0, ht0))
            images = [img_l, img_r]
        else:
            images = [img_l]

        images = [cv2.resize(image, (image_size[1], image_size[0])) for image in images]
        images = torch.from_numpy(np.stack(images, 0))
        images = images.permute(0, 3, 1, 2).to(dtype=torch.float32)

        intrinsics = torch.as_tensor(intrinsics_vec)
        intrinsics[0] *= image_size[1] / wd0
        intrinsics[1] *= image_size[0] / ht0
        intrinsics[2] *= image_size[1] / wd0
        intrinsics[3] *= image_size[0] / ht0

        data_list.append((stride*t, images, intrinsics))

    return data_list


def save_reconstruction(droid, reconstruction_path: str, ply_path: str, scale_factor=1.0):
    """
    Saves the reconstruction and/or point cloud

    Params
      droid: DROID-SLAM instance
      reconstruction_path: path to save reconstruction blob
      ply_path: path to save map as a PLY file
      scale_factor: scale for the PLY file
    """

    if hasattr(droid, "video2"):
        video = droid.video2
    else:
        video = droid.video

    t = video.counter.value
    save_data = {
        "tstamps": video.tstamp[:t].cpu(),
        "images": video.images[:t].cpu(),
        "disps": video.disps_up[:t].cpu(),
        "poses": video.poses[:t].cpu(),
        "intrinsics": video.intrinsics[:t].cpu()
    }

    if reconstruction_path is not None:
        torch.save(save_data, reconstruction_path)

    if ply_path is not None:
        filter_thresh = 0.005
        filter_count = 3

        images = save_data["images"].cuda()[...,::2,::2]
        disps = save_data["disps"].cuda()[...,::2,::2]
        poses = save_data["poses"].cuda()
        intrinsics = 4 * save_data["intrinsics"].cuda()

        disps = disps.contiguous()

        index = torch.arange(len(images), device="cuda")
        thresh = filter_thresh * torch.ones_like(disps.mean(dim=[1,2]))

        with CudaTimer("iproj"):
            points = droid_backends.iproj(SE3(poses).inv().data, disps, intrinsics[0])
        colors = images[:,[2,1,0]].permute(0,2,3,1) / 255.0

        with CudaTimer("filter"):
            counts = droid_backends.depth_filter(poses, disps, intrinsics[0], index, thresh)

        mask = (counts >= filter_count) & (disps > .25 * disps.mean())
        points_np = points[mask].cpu().numpy()
        points_np *= scale_factor
        colors_np = colors[mask].cpu().numpy()

        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points_np)
        point_cloud.colors = o3d.utility.Vector3dVector(colors_np)

        o3d.io.write_point_cloud(ply_path, point_cloud, write_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath", help="path to input rig")
    parser.add_argument("--gt", help="path to gt file")
    parser.add_argument("--weights", default="droid.pth")
    parser.add_argument("--buffer", type=int, default=512)
    parser.add_argument("--image_size", default=[320,512])
    parser.add_argument("--disable_vis", action="store_true")
    parser.add_argument("--stereo", action="store_true")

    parser.add_argument("--beta", type=float, default=0.3)
    parser.add_argument("--filter_thresh", type=float, default=2.4)
    parser.add_argument("--warmup", type=int, default=15)
    parser.add_argument("--keyframe_thresh", type=float, default=3.0)
    parser.add_argument("--frontend_thresh", type=float, default=17.5)
    parser.add_argument("--frontend_window", type=int, default=20)
    parser.add_argument("--frontend_radius", type=int, default=2)
    parser.add_argument("--frontend_nms", type=int, default=1)

    parser.add_argument("--backend_thresh", type=float, default=24.0)
    parser.add_argument("--backend_radius", type=int, default=2)
    parser.add_argument("--backend_nms", type=int, default=2)

    parser.add_argument("--upsample", action="store_true")
    parser.add_argument("--asynchronous", action="store_true")
    parser.add_argument("--frontend_device", type=str, default="cuda")
    parser.add_argument("--backend_device", type=str, default="cuda")
    parser.add_argument("--reconstruction", help="path to save reconstruction")
    parser.add_argument("--ply", help="path to saved reconstruction")
    args = parser.parse_args()

    timestamps_path = os.path.join(args.datapath, "timestamps.txt")
    tstamps = read_timestamps(timestamps_path)

    torch.multiprocessing.set_start_method('spawn')

    # need high resolution depths
    if args.ply is not None or args.reconstruction is not None:
        args.upsample = True

    print("Running evaluation on {}".format(args.datapath))
    print(args)

    droid = DroidAsync(args) if args.asynchronous else Droid(args)
    scene = Path(args.datapath).name

    images = image_stream(args.datapath, stereo=args.stereo, stride=1)

    # run with stride 2
    for (t, image, intrinsics) in tqdm(images[::2], desc=scene):
        droid.track(t, image, intrinsics=intrinsics)

    # fill in missing poses with stride 1
    traj_est = droid.terminate(images)

    if args.stereo:
        # Camera baseline is hard coded to 0.1m
        baseline = load_settings.read_baseline(Path(args.datapath) / "settings.yaml")
        stereo_scale_factor = baseline/0.1

        traj_est[:, :3] *= stereo_scale_factor
    else:
        stereo_scale_factor = 1.0

    if args.ply is not None or args.reconstruction is not None:
        save_reconstruction(droid, args.reconstruction, args.ply, 1.0)

    # Output TUM format trajectory file

    from evo.core.trajectory import PoseTrajectory3D
    from evo.tools import file_interface

    traj_est = PoseTrajectory3D(
        positions_xyz=traj_est[:,:3],
        orientations_quat_wxyz=traj_est[:,3:],
        timestamps=np.array(tstamps))

    file_interface.write_tum_trajectory_file("DROIDCameraTrajectory.txt", traj_est)

