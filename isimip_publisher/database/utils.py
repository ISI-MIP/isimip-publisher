import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from isimip_publisher.database.models import Base, Dataset, File

from isimip_publisher.utils import order_dict
from isimip_publisher.utils.checksum import get_checksum, get_checksum_type

logger = logging.getLogger(__name__)


def init_database_session():
    engine = create_engine(os.getenv('DATABASE'))

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()


def insert_dataset(session, dataset_name, metadata, version):
    attributes = order_dict(metadata)

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.name == dataset_name,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        if dataset.attributes != attributes:
            dataset.attributes = attributes
            logger.debug('update dataset %s', dataset_name)
        else:
            logger.debug('skip dataset %s', dataset_name)

        # raise RuntimeError('A dataset with the name %s and the version %s already exists' % (dataset_name, version))
    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', dataset_name)
        dataset = Dataset(
            name=dataset_name,
            version=version,
            attributes=attributes
        )
        session.add(dataset)


def insert_file(session, file_path, dataset_name, metadata, version):
    file_name = os.path.basename(file_path)
    checksum = get_checksum(file_path)
    checksum_type = get_checksum_type()
    attributes = order_dict(metadata)

    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.name == dataset_name,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' % (dataset_name, version))

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == file_path,
        File.version == version
    ).one_or_none()

    if file:
        if file.checksum == checksum:
            # the file has not changed
            if file.attributes != attributes:
                file.attributes = attributes
                logger.debug('update file %s', file_name)
            else:
                logger.debug('skip file %s', file_name)

        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % file_name)
    else:
        # insert a new row for this file
        logger.debug('insert file %s', file_name)
        file = File(
            name=file_name,
            version=version,
            path=file_path,
            checksum=checksum,
            checksum_type=checksum_type,
            attributes=attributes,
            dataset=dataset
        )
        session.add(file)
