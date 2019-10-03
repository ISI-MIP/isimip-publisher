from ..utils import get_subparser_title, add_version_to_path
from ..utils.config import parse_config, parse_filelist, parse_version
from ..utils.files import list_local_files, rename_file
from ..utils.metadata import get_netcdf_metadata
from ..utils.netcdf import update_netcdf_global_attributes
from ..utils.patterns import match_file


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

    for file_path in list_local_files(config, filelist):
        file_name, identifiers = match_file(config, file_path)
        metadata = get_netcdf_metadata(config, identifiers)
        update_netcdf_global_attributes(config, metadata, file_path)

        version_file_path = add_version_to_path(file_path, version)
        if version_file_path != file_path:
            rename_file(file_path, version_file_path)
