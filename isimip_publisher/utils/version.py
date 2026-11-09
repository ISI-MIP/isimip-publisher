import logging
import re

logger = logging.getLogger(__name__)

# version in YYYYMMDD format, optionally prefixed with 'v' (e.g. v20240101)
ISIMIP_VERSION_PATTERN = re.compile(r'^v?(\d{8})$')


def get_version(dataset, version=None):
    versions = [file.version for file in dataset.files]

    # check if files with a version and files without version are mixed
    if any(value is None for value in versions) and any(value is not None for value in versions):
        missing = [file.path for file in dataset.files if file.version is None]
        raise RuntimeError(f'Not all files of the dataset {dataset.path} have an ISIMIP version, missing in: {missing}')

    values = {value for value in versions if value is not None}

    # check if we have more than one version
    if len(values) > 1:
        raise RuntimeError(f'Dataset {dataset.path} has conflicting versions: {sorted(values)}')

    # if we have a version, validate it and use that instead of the version provided via the settings
    if values:
        value = values.pop()

        match = ISIMIP_VERSION_PATTERN.match(str(value))

        if match is None:
            raise RuntimeError(f'Invalid ISIMIP version {value!r} in {dataset.path}, should be YYYYMMDD or vYYYYMMDD')

        version = match.group(1)
        logger.info(f'Using version {version} from the global attributes of {dataset.path}')

    return version
