import argparse
from neurd.vdi_microns import volume_data_interface as vdi
from datasci_tools import system_utils as su



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--segment_id", default=864691136361538530, help="id of segment to download")
    parser.add_argument("--base_dir", default = "", help="base directory to save results in. Must end with /")
    args = parser.parse_args()

    segment_id = args.segment_id
    base_dir = args.base_dir

    mesh_decimated = vdi.fetch_segment_id_mesh(
        mesh_filepath = f"{base_dir}{segment_id}_decimated.off"
    )

    products = su.load_object(
        f"{base_dir}{segment_id}_products.pkl"
    )

    neuron_obj = vdi.load_neuron_obj(
        segment_id = segment_id,
        mesh_decimated = mesh_decimated
    )

    multi_soma_split_parameters = dict()

    _ = neuron_obj.calculate_multi_soma_split_suggestions(
        plot = False,
        store_in_obj = True,
        **multi_soma_split_parameters,
        verbose=True
    )

    neuron_obj.pipeline_products.multi_soma_split_suggestions.multi_soma_split_parameters = multi_soma_split_parameters

    vdi.save_neuron_obj(
        neuron_obj,
        directory=base_dir,
        verbose = True
    )

    neuron_list = neuron_obj.multi_soma_split_execution(
        verbose = False,
    )

    for i, n in enumerate(neuron_list):
        vdi.save_neuron_obj(
            n,
            directory=base_dir,
            suffix=f"_split_{i}.pbz2"
        )

