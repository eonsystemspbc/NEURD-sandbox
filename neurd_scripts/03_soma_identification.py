from neurd import soma_extraction_utils as sm
from neurd.vdi_microns import volume_data_interface as vdi
from datasci_tools import system_utils as su
import argparse



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

    soma_extraction_parameters = dict()

    soma_products = sm.soma_indentification(
        mesh_decimated,
        verbose=verbose,
        **soma_extraction_parameters
    )

    products = su.load_object(
        f"{base_dir}{segment_id}_products.pkl"
    )

    products.set_stage_attrs(
        stage = "soma_identification",
        attr_dict = soma_products,
    )

    su.save_object(
        products, 
        f"{base_dir}{segment_id}_products.pkl"
    )
