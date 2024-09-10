import numpy as np 
import kimimaro
from glob import glob
import argparse
from em_erl.erl import skel_to_erlgraph
from em_erl.eval import compute_erl_score


def load_data(path):
    """
    Helper function to load all npy and npz files in a directory into a single numpy array.
    Requires all files to have the same shape.

    Parameters
    ----------
    path : str
        The path to the directory containing the npy and npz files.

    Returns
    -------
    np.ndarray
        A numpy array containing the loaded data.
    """
    files = sorted(glob(path + "*.npy"))

    data_shape = np.load(files[0]).shape

    out = np.zeros((len(files), data_shape[0], data_shape[1]), dtype=int)

    for i, f in enumerate(files):
        out[i, :, :] = np.load(f)

    return out

# Stolen from PytorchConnectomics/em_erl
# https://github.com/PytorchConnectomics/em_erl/blob/main/em_erl/eval.py
def compute_segment_lut(
    segment, node_position, mask=None, chunk_num=1, data_type=np.uint32
):
    """
    The function `compute_segment_lut` is a low memory version of a lookup table
    computation for node segments in a 3D volume.

    :param node_position: A numpy array containing the coordinates of each node. The shape of the array
    is (N, 3), where N is the number of nodes and each row represents the (z, y, x) coordinates of a
    node
    :param segment: either a 3D volume or a string representing the
    name of a file containing segment data.
    :param chunk_num: The parameter `chunk_num` is the number of chunks into which the volume is divided
    for reading. It is used in the `read_vol` function to specify which chunk to read, defaults to 1
    (optional)
    :param data_type: The parameter `data_type` is the data type of the array used to store the node segment
    lookup table. In this case, it is set to `np.uint32`, which means the array will store unsigned
    32-bit integers
    :return: a list of numpy arrays, where each array represents the node segment lookup table for a
    specific segment.
    """
    if not isinstance(segment, str):
        # load the whole segment
        node_lut = segment[
            node_position[:, 0], node_position[:, 1], node_position[:, 2]
        ]
        mask_id = []
        if mask is not None:
            if isinstance(mask, str):
                mask = read_vol(mask)
            mask_id = segment[mask > 0]
    else:
        # read segment by chunk (when memory is limited)
        assert ".h5" in segment
        node_lut = np.zeros(node_position.shape[0], data_type)
        mask_id = [[]] * chunk_num
        start_z = 0
        for chunk_id in range(chunk_num):
            seg = read_vol(segment, None, chunk_id, chunk_num)
            last_z = start_z + seg.shape[0]
            ind = (node_position[:, 0] >= start_z) * (node_position[:, 0] < last_z)
            pts = node_position[ind]
            node_lut[ind] = seg[pts[:, 0] - start_z, pts[:, 1], pts[:, 2]]
            if mask is not None:
                if isinstance(mask, str):
                    mask_z = read_vol(mask, None, chunk_id, chunk_num)
                else:
                    mask_z = mask[start_z:last_z]
                mask_id[chunk_id] = seg[mask_z > 0]
            start_z = last_z
        if mask is not None:
            # remove irrelevant seg ids (not used by nodes)
            node_lut_unique = np.unique(node_lut)
            for chunk_id in range(chunk_num):
                mask_id[chunk_id] = mask_id[chunk_id][
                    np.in1d(mask_id[chunk_id], node_lut_unique)
                ]
        mask_id = np.concatenate(mask_id)
    return node_lut, mask_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gt_path", help="path to ground truth segmentation directory", required=True)
    parser.add_argument("--proof_path", help="path to proofread segmentation directory", required=True)
    parser.add_argument("--anisotropy", default=(40, 4, 4), help="pixel size in nm. Format: (x, y, z)")
    args = parser.parse_args()

    gt_seg = load_data(args.gt_path)
    proof_seg = load_data(args.proof_path)
    anisotropy = args.anisotropy

    gt_skels = kimimaro.skeletonize(
        gt_seg, 
        teasar_params={
            "scale": 1.5, 
            "const": 300, # physical units
            "pdrf_scale": 100000,
            "pdrf_exponent": 4,
            "soma_acceptance_threshold": 3500, # physical units
            "soma_detection_threshold": 750, # physical units
            "soma_invalidation_const": 300, # physical units
            "soma_invalidation_scale": 2,
            "max_paths": 300, # default None
        },
        dust_threshold=1000, # skip connected components with fewer than this many voxels
        anisotropy=anisotropy, # default True
        fix_branching=True, # default True
        fix_borders=True, # default True
        fill_holes=True, # default False
        fix_avocados=True, # default False
        progress=True, # default False, show progress bar
        parallel=1, # <= 0 all cpu, 1 single process, 2+ multiprocess
        parallel_chunk_size=100, # how many skeletons to process before updating progress bar
        )

    gt_graph = skel_to_erlgraph(gt_skels)

    proof_skels = kimimaro.skeletonize(
        proof_seg, 
        teasar_params={
            "scale": 1.5, 
            "const": 300, # physical units
            "pdrf_scale": 100000,
            "pdrf_exponent": 4,
            "soma_acceptance_threshold": 3500, # physical units
            "soma_detection_threshold": 750, # physical units
            "soma_invalidation_const": 300, # physical units
            "soma_invalidation_scale": 2,
            "max_paths": 300, # default None
        },
        dust_threshold=1000, # skip connected components with fewer than this many voxels
        anisotropy=anisotropy, # default True
        fix_branching=True, # default True
        fix_borders=True, # default True
        fill_holes=True, # default False
        fix_avocados=True, # default False
        progress=True, # default False, show progress bar
        parallel=1, # <= 0 all cpu, 1 single process, 2+ multiprocess
        parallel_chunk_size=100, # how many skeletons to process before updating progress bar
        )

    proof_graph = skel_to_erlgraph(proof_skels)

    nodes_position = proof_graph.get_nodes_position(anisotropy)

    node_segment_lut, mask_segment_id = compute_segment_lut(gt_seg, nodes_position)

    score = compute_erl_score(erl_graph=gt_graph,
    node_segment_lut=node_segment_lut,
    mask_segment_id=mask_segment_id,
    merge_threshold=0,
    verbose=True)

    score.compute_erl(None)

    score.print_erl()

    

   


    