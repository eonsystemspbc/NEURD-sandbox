from caveclient import CAVEclient
import imageryclient as ic
from tqdm import tqdm
import numpy as np
import pickle

if __name__ == "__main__":
    # This script downloads segmentations around somas of neurons that were proofread in newer versions of microns and 
    # compares them to the unproofread segmentations. The goal is to calculate how much segmentations overlap to get a 
    # sense of which neurons could be useful prototypes for proofreading.
    # Data are downloaded in a large area in low quality to ensure that regions outside of somas are included. An issue
    # with this early approach is that errors are commonly around more distal, thin processes and not around the soma 
    # center.

    # Connect to database
    client = CAVEclient('minnie65_public')
    old_client = CAVEclient('minnie65_public_v117')

    # collect neurons that have been manually proofread
    old_proofreads = old_client.materialize.query_table('proofreading_status_public_release', split_positions=True)
    new_proofreads = client.materialize.query_table('proofreading_status_and_strategy', split_positions=True)

    # we're interested in cells that were proofread in the newest version, but not in the older one
    cells_of_interest = new_proofreads[~new_proofreads["pt_root_id"].isin(old_proofreads["pt_root_id"])]
    # so that no renaming occurs
    cells_of_interest = cells_of_interest[~cells_of_interest["pt_position_x"].isin(old_proofreads["pt_position_x"])]
    cells_of_interest = cells_of_interest[~cells_of_interest["pt_position_y"].isin(old_proofreads["pt_position_y"])]
    cells_of_interest = cells_of_interest[~cells_of_interest["pt_position_z"].isin(old_proofreads["pt_position_z"])]

    cells_of_interest = cells_of_interest.reset_index()


    # Download segmentation around each soma
    size = 1024*4
    depth = 256

    img_client = ic.ImageryClient(client=client)
    img_client_old = ic.ImageryClient(client=old_client)

    overlaps = dict()
    skipped_cells = []

    # One intersting inhibitory neuron
    idx = cells_of_interest[cells_of_interest["pt_root_id"] == 864691135526405723].index[0]
    x, y, z = cells_of_interest.iloc[idx][["pt_position_x", "pt_position_y", "pt_position_z"]]

    ctr = [x, y, z]

    # Collect old segmentation in low res
    old_segs = img_client_old.segmentation_cutout(ctr, bbox_size=(size,size, depth), mip=3)

    # Label of cell will be most common label in segmentation
    label, counts = np.unique(old_segs, return_counts=True)
    cell_label_old = label[np.argmax(counts)]

    # Repeat for new segmentation
    segs = img_client.segmentation_cutout(ctr, bbox_size=(size,size, depth), mip=3)

    label, counts = np.unique(segs, return_counts=True)
    cell_label_new = label[np.argmax(counts)]

    # Calculate which proportion of pixel classification remained the same
    overlap = len(segs[(segs == cell_label_new) & (old_segs == cell_label_old)]) / np.max(counts)
    print(f"{i}: {overlap}")

    overlaps[i] = overlap
