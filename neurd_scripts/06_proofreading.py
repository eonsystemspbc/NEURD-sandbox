import argparse
from neurd.vdi_microns import volume_data_interface as vdi
from neurd import neuron_utils as nru
from neurd import neuron_pipeline_utils as npu


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--segment_id", default=864691136361538530, help="id of segment to download")
    parser.add_argument("--base_dir", default = "", help="base directory to save results in. Must end with /")
    parser.add_argument("--split_num", default=1, help="split to proofread")
    args = parser.parse_args()

    segment_id = int(args.segment_id)
    base_dir = args.base_dir
    split_num = args.split_num

    synapse_filepath = str(Path(f'{base_dir}{segment_id}_synapses.csv').absolute())
    
    vdi.set_synapse_filepath(
        synapse_filepath
    )

    mesh_decimated = vdi.fetch_segment_id_mesh(
        mesh_filepath = f"{base_dir}{segment_id}_decimated.off"
    )

    neuron_obj_path = Path(f"{base_dir}{segment_id}_split_{split_num}.pbz2")
    
    if not neuron_obj_path.exists():
        raise Exception(f"Could not find neuron object at {neuron_obj_path}")

    neuron_obj = nru.decompress_neuron(
        filepath = neuron_obj_path,
        original_mesh = mesh_decimated, 
        suppress_output = False
    )

    neuron_obj_axon = npu.cell_type_ax_dendr_stage(
        neuron_obj,
        mesh_decimated = mesh_decimated,
        plot_axon = False,
    )

    vdi.save_neuron_obj(
        neuron_obj_axon,
        suffix=f"_split_{i}_axon.pbz2",
    )

    neuron_obj_proof = npu.auto_proof_stage(
        neuron_obj_axon,
        mesh_decimated = mesh_decimated,
        calculate_after_proof_stats = True,
    )

    vdi.save_neuron_obj_auto_proof(
        neuron_obj_proof,
        suffix=f"_split_{i}_proofread.pbz2",
    )


    