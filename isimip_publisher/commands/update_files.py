from isimip_publisher.netcdf.utils import update_netcdf_global_attributes

from isimip_publisher.utils import get_subparser_title
from isimip_publisher.utils.config import parse_config, parse_filelist, parse_version
from isimip_publisher.utils.files import list_local_files, add_version_to_file
from isimip_publisher.utils.validation import validate_file
from isimip_publisher.utils.metadata import get_netcdf_metadata


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
