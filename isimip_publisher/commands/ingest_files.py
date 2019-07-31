from ..utils import get_subparser_title
from ..utils.config import parse_config, parse_filelist, parse_version
from ..utils.database import init_database_session, insert_file
from ..utils.datasets import find_dataset_for_file
from ..utils.files import list_local_files
from ..utils.metadata import get_file_metadata
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
    files = list_local_files(config, filelist)

    session = init_database_session()

    for file in files:
        identifiers = validate_file(config, file)
        metadata = get_file_metadata(config, identifiers)
        dataset, _ = find_dataset_for_file(config, file)

        insert_file(session, file, dataset, metadata, version)

    session.commit()
