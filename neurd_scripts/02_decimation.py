from neurd.vdi_microns import volume_data_interface as vdi
from datasci_tools import pipeline
from mesh_tools import trimesh_utils as tu
from datasci_tools import system_utils as su
import trimesh
import argparse
import os


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--segment_id", default=864691136361538530, help="id of segment to download")
    parser.add_argument("--base_dir", default = "", help="base directory to save results in. Must end with /")
    parser.add_argument("--decimation_ratio", default=0.062, help="ratio by which to decimate mesh")
    args = parser.parse_args()

    segment_id = args.segment_id
    base_dir = args.base_dir
    decimation_ratio = args.decimation_ratio

    mesh = vdi.fetch_segment_id_mesh(
        segment_id,
    )

    if os.path.exists(f"{base_dir}{segment_id}_products.pkl"):
        products = load_object(f"{base_dir}{segment_id}_products.pkl")
    else:
        products = pipeline.PipelineProducts()

    decimation_parameters = dict(
        decimation_ratio = decimation_ratio
    )

    mesh_decimated = tu.decimate(
        mesh,
        **decimation_parameters
    )

    with open(f"{base_dir}{segment_id}_decimated.off", "wb") as f:
        trimesh.exchange.export.export_mesh(mesh_decimated, f, file_type='off')

    products.set_stage_attrs(
        stage = "decimation",
        attr_dict = dict(
            decimation_parameters = decimation_parameters,
            segment_id = segment_id,
        ),
    )

    su.save_object(
        products, 
        f"{base_dir}{segment_id}_products.pkl"
    )