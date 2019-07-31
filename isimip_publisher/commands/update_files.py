from ..utils import get_subparser_title
from ..utils.config import parse_config, parse_filelist, parse_version
from ..utils.files import add_version_to_file, list_local_files
from ..utils.metadata import get_netcdf_metadata
from ..utils.netcdf import update_netcdf_global_attributes
from ..utils.validation import validate_file


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')
    parser.set_defaults(func=main)


def main(args):
    version = parse_version(args.version)
    config = parse_config(args.simulation_round, args.sector, args.model, version)
    filelist = parse_filelist(args.filelist_file)

    for file in list_local_files(config, filelist):
        identifiers = validate_file(config, file)
        metadata = get_netcdf_metadata(config, identifiers)
        update_netcdf_global_attributes(config, metadata, file)
        add_version_to_file(file, version)
