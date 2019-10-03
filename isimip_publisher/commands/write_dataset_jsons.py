from ..utils import get_subparser_title, add_version_to_path
from ..utils.config import parse_config, parse_filelist, parse_version
from ..utils.datasets import find_datasets
from ..utils.files import list_local_files
from ..utils.json import write_dataset_json
from ..utils.metadata import get_dataset_metadata


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')
    parser.set_defaults(func=main)


def main(args):
    version = parse_version(args.version)
    config = parse_config(args.simulation_round, args.product, args.sector, args.model, version)
    filelist = parse_filelist(args.filelist_file)
    files = list_local_files(config, filelist)
    datasets = find_datasets(config, files)

    for dataset_path, dataset in datasets.items():
        metadata = get_dataset_metadata(config, dataset['identifiers'])
        dataset_version_path = add_version_to_path(dataset_path, version)
        write_dataset_json(config, metadata, dataset_version_path)
