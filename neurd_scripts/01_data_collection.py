from cloudvolume import CloudVolume
from caveclient import CAVEclient
import pandas as pd
import trimesh
import argparse




def download_mesh(segment_id, base_dir=""):
    
    # Set up oldest cloudvolume to collect mesh
    cv = CloudVolume('precomputed://https://storage.googleapis.com/iarpa_microns/minnie/minnie65/seg',
                    progress=False, # shows progress bar
                    cache=False, # cache to disk to avoid repeated downloads
                    fill_missing=False,)


    # download mesh
    mesh = cv.mesh.get(segment_id)[segment_id]

    with open(f"{base_dir}{segment_id}.off", "wb") as f:
        trimesh.exchange.export.export_mesh(mesh, f, file_type='off')


def collect_synapses(segment_id, base_dir):
    """
    Function to collect all pre and postsynaptic endings involving neuron segment_id from client and save results as a csv file named segment_id_synapses.csv

    Parameters
    ----------
    segment_id : int
        ID of neuron segment to collect synapses from
    client : CAVEclient
        Client with synapse information. Currently only supports microns data
    """
    client = CAVEclient('minnie65_public')
    client.version=117
    # Get synapses going from segment_id to other neurons
    pre_synapses = client.materialize.synapse_query(pre_ids = segment_id, split_positions=True)
    pre_synapses = pre_synapses[["pre_pt_root_id", "post_pt_root_id", "id", "pre_pt_position_x", "pre_pt_position_y", "pre_pt_position_z", "size"]]
    pre_synapses["prepost"] = "presyn"
    # rename columns to match neurd synapse dataframes
    rename_map = {
        "pre_pt_root_id" : "segment_id",
        "post_pt_root_id" : "segment_id_secondary",
        "id" : "synapse_id",
        "pre_pt_position_x" : "synapse_x",
        "pre_pt_position_y" : "synapse_y",
        "pre_pt_position_z" : "synapse_z",
        "size" : "synapse_size",
    }
    pre_synapses = pre_synapses.rename(columns = rename_map)
    # save synapses so far
    pre_synapses.to_csv(f"{base_dir}{segment_id}_synapses.csv")

    # get all synapses connection to neuron segment_id
    post_synapses = client.materialize.synapse_query(post_ids = segment_id, split_positions=True)

    post_synapses = post_synapses[["pre_pt_root_id", "post_pt_root_id", "id", "post_pt_position_x", "post_pt_position_y", "post_pt_position_z", "size"]]
    post_synapses["prepost"] = "postsyn"
    rename_map = {
        "post_pt_root_id" : "segment_id",
        "pre_pt_root_id" : "segment_id_secondary",
        "id" : "synapse_id",
        "post_pt_position_x" : "synapse_x",
        "post_pt_position_y" : "synapse_y",
        "post_pt_position_z" : "synapse_z",
        "size" : "synapse_size",
    }
    post_synapses = post_synapses.rename(columns = rename_map)
    # append to previously created dataframe
    post_synapses.to_csv(f"{base_dir}{segment_id}_synapses.csv", mode="a", header=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--segment_id", default=864691136361538530, help="id of segment to download")
    parser.add_argument("--base_dir", default = "", help="base directory to save results in. Must end with /")
    args = parser.parse_args()

    segment_id = int(args.segment_id)
    base_dir = args.base_dir

    download_mesh(segment_id, base_dir)

    collect_synapses(segment_id, base_dir)