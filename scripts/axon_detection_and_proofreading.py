import neurd
from mesh_tools import trimesh_utils as tu
from datasci_tools import ipyvolume_utils as ipvu
from neurd import neuron_visualizations as nviz
from pathlib import Path
from cloudvolume import CloudVolume
import trimesh
from datasci_tools import system_utils as su
from neurd.vdi_microns import volume_data_interface as vdi
from neurd import neuron_pipeline_utils as npu




def main():
    # This script can be run with neurd for the final two steps of proofreading. 
    # It requires a decimated mesh as a .off file, previous pipeline products and a synapse .csv file.
    segment_id = 864691135212863360
    mesh_decimated = tu.load_mesh_no_processing(f"{segment_id}.off")
    products = su.load_object("products_up_to_soma_stage")
    synapse_filepath = str(Path(f'./{segment_id}_synapses.csv').absolute())
    vdi.set_synapse_filepath(
        synapse_filepath
    )

    neuron_obj_rec = vdi.load_neuron_obj(
        segment_id = segment_id,
        mesh_decimated = mesh_decimated
    )

    neuron_obj_axon = npu.cell_type_ax_dendr_stage(
        neuron_obj_rec,
        mesh_decimated = mesh_decimated,
        plot_axon = False,
        verbose=True
    )

    neuron_obj_proof = npu.auto_proof_stage(
        neuron_obj_axon,
        mesh_decimated = mesh_decimated,
        calculate_after_proof_stats = False,
    )

    _ = npu.after_auto_proof_stats(
        neuron_obj_proof,
        store_in_obj = True,
    )

    vdi.save_neuron_obj_auto_proof(
        neuron_obj_proof,
    )


if __name__ == "__main__":
    main()