from neurd.vdi_microns import volume_data_interface as vdi
from datasci_tools import system_utils as su
from neurd import neuron
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--segment_id", default=864691136361538530, help="id of segment to download")
    parser.add_argument("--base_dir", default = "", help="base directory to save results in. Must end with /")
    args = parser.parse_args()

    segment_id = int(args.segment_id)
    base_dir = args.base_dir

    mesh_decimated = vdi.fetch_segment_id_mesh(
        mesh_filepath = f"{base_dir}{segment_id}_decimated.off"
    )

    products = su.load_object(
        f"{base_dir}{segment_id}_products.pkl"
    )

    neuron_obj = neuron.Neuron(
        mesh = mesh_decimated,
        segment_id = segment_id, # don't need this explicitely if segment_id is already in products
        pipeline_products = products,
        suppress_preprocessing_print=False,
        suppress_output=False,
    )

    _ = neuron_obj.calculate_decomposition_products(
        store_in_obj = True,
    )

    vdi.save_neuron_obj(
        neuron_obj,
        directory=base_dir,
        verbose = True
    )

